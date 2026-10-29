"""Article service encapsulating business logic."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateError, NotFoundError
from app.core.logging import get_logger
from app.models.article import Article
from app.repositories.article_repo import ArticleRepository
from app.schemas.article import ArticleCreate, ArticleUpdate

logger = get_logger(__name__)


class ArticleService:
    """Service layer for article operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.repo = ArticleRepository(session)
        self.session = session

    async def get_article(self, article_id: UUID) -> Article:
        """Fetch a single article by ID.

        Args:
            article_id: The article's UUID.

        Returns:
            The Article instance.

        Raises:
            NotFoundError: If the article does not exist.
        """
        return await self.repo.get_by_id(article_id)

    async def list_articles(
        self,
        *,
        source: str | None = None,
        sentiment: str | None = None,
        sector: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        search: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[Sequence[Article], int]:
        """List articles with optional filters and pagination.

        Args:
            source: Filter by source name.
            sentiment: Filter by sentiment label.
            sector: Filter by sector entity.
            date_from: Minimum publication date.
            date_to: Maximum publication date.
            search: Title search string.
            page: Page number (1-based).
            limit: Page size.

        Returns:
            Tuple of (articles, total_count).
        """
        offset = (page - 1) * limit
        return await self.repo.list_filtered(
            source=source,
            sentiment=sentiment,
            sector=sector,
            date_from=date_from,
            date_to=date_to,
            search=search,
            offset=offset,
            limit=limit,
        )

    async def create_article(self, data: ArticleCreate) -> Article:
        """Create a new article if it doesn't already exist.

        Args:
            data: Article creation schema.

        Returns:
            The created Article.

        Raises:
            DuplicateError: If an article with the same source_url exists.
        """
        if await self.repo.source_url_exists(data.source_url):
            raise DuplicateError("Article", data.source_url)

        article = Article(
            title=data.title,
            content=data.content,
            source=data.source,
            source_url=data.source_url,
            published_at=data.published_at,
            metadata_=data.metadata_ or {},
        )
        return await self.repo.create(article)

    async def update_article(self, article_id: UUID, data: ArticleUpdate) -> Article:
        """Update an article's enrichment fields.

        Args:
            article_id: The article's UUID.
            data: Fields to update.

        Returns:
            The updated Article.
        """
        update_values = data.model_dump(exclude_unset=True, by_alias=False)
        if not update_values:
            return await self.repo.get_by_id(article_id)
        return await self.repo.update_by_id(article_id, update_values)

    async def check_duplicate(self, source_url: str) -> bool:
        """Check if an article URL has already been ingested.

        Args:
            source_url: URL to check.

        Returns:
            True if already exists.
        """
        return await self.repo.source_url_exists(source_url)

    async def get_recent_articles(self, since: datetime, limit: int = 100) -> Sequence[Article]:
        """Fetch articles published since a given datetime.

        Args:
            since: Cutoff datetime.
            limit: Max results.

        Returns:
            List of articles.
        """
        return await self.repo.get_articles_since(since, limit)

    async def get_top_articles(self, limit: int = 10) -> Sequence[Article]:
        """Fetch top articles by impact score.

        Args:
            limit: Max results.

        Returns:
            List of top-impact articles.
        """
        return await self.repo.get_top_articles(limit)

    async def process_and_save_raw_article(self, raw_article: dict[str, Any]) -> Article:
        """Process a raw article through the agent pipeline and save the results.

        This runs Summarization, Sentiment, Entity, Event, and Impact agents
        sequentially, links entities and events, generates embeddings, and
        stores the article vector in Qdrant.
        """
        # 1. Resolve imports locally to avoid circular dependencies
        from app.agents.summarization_agent import SummarizationAgent
        from app.agents.sentiment_agent import SentimentAgent
        from app.agents.entity_agent import EntityExtractionAgent
        from app.agents.event_agent import EventDetectionAgent
        from app.agents.impact_agent import ImpactScoringAgent
        from app.infrastructure.embeddings import embed_document
        from app.infrastructure.qdrant_client import upsert_vector
        from app.models.entity import Entity
        from app.models.event import Event

        title = raw_article.get("title", "")
        content = raw_article.get("content", "")
        source = raw_article.get("source", "")
        source_url = raw_article.get("source_url", "")
        
        if source_url:
            from sqlalchemy import select
            stmt = select(Article).where(Article.source_url == source_url)
            res = await self.session.execute(stmt)
            existing_article = res.scalar_one_or_none()
            if existing_article:
                logger.info("article_already_exists_skipping", source_url=source_url)
                return existing_article
        
        published_at = None
        if raw_article.get("published_at"):
            try:
                published_at = datetime.fromisoformat(raw_article["published_at"])
            except ValueError:
                published_at = datetime.utcnow()

        logger.info("processing_raw_article_start", title=title[:80])

        from uuid import uuid4
        # Initialize the Article object first
        article = Article(
            id=uuid4(),
            title=title,
            content=content,
            source=source,
            source_url=source_url,
            published_at=published_at,
            metadata_={},
        )
        self.session.add(article)

        # 2. Run Summarization Agent
        try:
            sum_agent = SummarizationAgent()
            sum_out = await sum_agent.process({"title": title, "content": content})
            article.summary = sum_out.summary
            article.metadata_["key_takeaways"] = sum_out.key_takeaways
            article.metadata_["market_relevance"] = sum_out.market_relevance
        except Exception as exc:
            logger.error("pipeline_summarization_failed", error=str(exc))
            article.summary = content[:200]
            sum_out = None

        # 3. Run Sentiment Agent
        try:
            sent_agent = SentimentAgent()
            sent_out = await sent_agent.process({"title": title, "summary": article.summary})
            article.sentiment = sent_out.sentiment
            article.sentiment_score = sent_out.score
            article.metadata_["sentiment_confidence"] = sent_out.confidence
            article.metadata_["sentiment_reasoning"] = sent_out.reasoning
        except Exception as exc:
            logger.error("pipeline_sentiment_failed", error=str(exc))
            article.sentiment = "neutral"
            article.sentiment_score = 0.0
            sent_out = None

        # 4. Run Entity Extraction Agent
        try:
            ent_agent = EntityExtractionAgent()
            ent_out = await ent_agent.process({"title": title, "content": content})
            
            # Map sectors and companies
            extracted_companies = [e.name for e in ent_out.entities if e.type == "company"]
            extracted_sectors = [e.name for e in ent_out.entities if e.type == "sector"]
            
            # Resolve companies
            for comp_name in extracted_companies:
                from sqlalchemy import select
                stmt = select(Entity).where(Entity.name == comp_name)
                res = await self.session.execute(stmt)
                entity_obj = res.scalar_one_or_none()
                if not entity_obj:
                    entity_obj = Entity(name=comp_name, type="company", confidence=1.0)
                    self.session.add(entity_obj)
                article.entities.append(entity_obj)

            # Resolve sectors
            for sec_name in extracted_sectors:
                from sqlalchemy import select
                stmt = select(Entity).where(Entity.name == sec_name)
                res = await self.session.execute(stmt)
                entity_obj = res.scalar_one_or_none()
                if not entity_obj:
                    entity_obj = Entity(name=sec_name, type="sector", confidence=1.0)
                    self.session.add(entity_obj)
                article.entities.append(entity_obj)
        except Exception as exc:
            logger.error("pipeline_entity_failed", error=str(exc))
            ent_out = None

        # 5. Run Event Detection Agent
        event_obj = None
        events_list = []
        try:
            evt_agent = EventDetectionAgent()
            evt_out = await evt_agent.process({"title": title, "content": content})
            if evt_out and evt_out.events:
                for evt in evt_out.events:
                    if evt.confidence > 0.4:
                        event_obj = Event(
                            article_id=article.id,
                            event_type=evt.event_type,
                            severity=evt.severity,
                            confidence=evt.confidence,
                            affected_entities=evt.affected_entities,
                            affected_sectors=evt.affected_sectors,
                        )
                        self.session.add(event_obj)
                        article.events.append(event_obj)
                        events_list.append({
                            "event_type": evt.event_type,
                            "severity": evt.severity,
                            "confidence": evt.confidence,
                            "affected_entities": evt.affected_entities,
                            "affected_sectors": evt.affected_sectors
                        })
        except Exception as exc:
            logger.error("pipeline_event_failed", error=str(exc))

        # 6. Run Impact Scoring Agent
        try:
            imp_agent = ImpactScoringAgent()
            scored_entities = [{"name": e.name, "type": e.type} for e in (ent_out.entities if ent_out else [])]
            imp_out = await imp_agent.process({
                "source": source,
                "sentiment_score": article.sentiment_score or 0.0,
                "events": events_list,
                "entities": scored_entities,
                "title": title,
                "content": content,
            })
            article.impact_score = imp_out.impact_score
        except Exception as exc:
            logger.error("pipeline_impact_failed", error=str(exc))
            article.impact_score = 50.0

        # 7. Generate embedding and index in Qdrant
        try:
            embedding_text = f"{title}\n\n{article.summary or ''}"
            vector = await embed_document(embedding_text)
            
            payload = {
                "article_id": str(article.id),
                "title": title,
                "content": content,
                "source": source,
                "source_url": source_url,
                "sentiment": article.sentiment,
                "event_type": event_obj.event_type if event_obj else None,
                "impact_score": article.impact_score,
                "published_at": article.published_at.isoformat() if article.published_at else None,
            }
            
            emb_id = await upsert_vector(
                article_id=str(article.id),
                vector=vector,
                payload=payload,
            )
            article.embedding_id = emb_id
        except Exception as exc:
            logger.error("pipeline_qdrant_indexing_failed", error=str(exc))

        # Commit transaction with rollback safety
        try:
            await self.session.commit()
            logger.info("processing_raw_article_success", article_id=str(article.id))
            return article
        except Exception as exc:
            logger.error("pipeline_commit_failed_rolling_back", error=str(exc))
            await self.session.rollback()
            raise
