"use client";

import * as React from "react";
import { MessageSquareCode, Send, Sparkles, AlertCircle, RefreshCw, Layers, Link as LinkIcon } from "lucide-react";
import { Shell } from "@/components/layout/shell";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, Input, Button, Badge } from "@/components/ui";
import { mockChatMessages, suggestedQuestions } from "@/lib/mock-data";
import { sendChatMessage } from "@/lib/api";
import type { ChatMessage, Citation } from "@/types";

export default function AskMarketIQPage() {
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [input, setInput] = React.useState<string>("");
  const [loading, setLoading] = React.useState<boolean>(false);
  const [conversationId, setConversationId] = React.useState<string | null>(null);
  const [isDemo, setIsDemo] = React.useState<boolean>(false);
  
  // Ref for auto-scrolling
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  // Load welcome recommendations
  React.useEffect(() => {
    // Add introductory system explanation as standard welcome message
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content: "Welcome to **MarketIQ Conversational Search**. I analyze ingested financial news, market events, and narrative trends using Retrieval-Augmented Generation.\n\nAsk me anything about market-moving events, company sentiment, or structural macro narratives.",
        timestamp: new Date().toISOString(),
      }
    ]);
  }, []);

  const handleSend = async (text: string) => {
    if (!text.trim() || loading) return;
    
    const userMsg: ChatMessage = {
      id: Math.random().toString(),
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // Fetch response from backend RAG API
      const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${apiBaseUrl}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: text,
          conversation_id: conversationId,
        }),
      });

      if (!response.ok) throw new Error("API Offline");

      const body = await response.json();
      
      if (body.success && body.data) {
        const assistantMsg: ChatMessage = {
          id: Math.random().toString(),
          role: "assistant",
          content: body.data.answer,
          citations: body.data.citations.map((c: any) => ({
            id: c.article_id,
            article_id: c.article_id,
            title: c.title,
            source: c.source,
            url: c.source_url,
            relevance_score: c.relevance_score,
          })),
          timestamp: new Date().toISOString(),
        };

        if (body.data.conversation_id) {
          setConversationId(body.data.conversation_id);
        }

        setMessages(prev => [...prev, assistantMsg]);
        setIsDemo(false);
      } else {
        throw new Error("Invalid response format");
      }
    } catch (err) {
      console.warn("API Offline or error, activating mock responses:", err);
      setIsDemo(true);
      
      // Simulate RAG response delay
      setTimeout(() => {
        // Find matching mock response or provide generic mock response
        const mockMatch = mockChatMessages.find(m => m.role === "assistant");
        
        const assistantMsg: ChatMessage = {
          id: Math.random().toString(),
          role: "assistant",
          content: mockMatch?.content || "Understood. The MarketIQ agent is offline but running in demo fallback. Here is the simulated response details.",
          citations: mockMatch?.citations || [],
          timestamp: new Date().toISOString(),
        };
        
        setMessages(prev => [...prev, assistantMsg]);
      }, 1500);
    } finally {
      // Delay disabling loader slightly for mock transitions
      setTimeout(() => {
        setLoading(false);
      }, 1000);
    }
  };

  return (
    <Shell>
      <div className="flex flex-col h-[calc(100vh-8rem)] max-w-4xl mx-auto space-y-6">
        {/* Chat History Panel */}
        <div className="flex-1 overflow-y-auto pr-2 space-y-6 max-h-[calc(100vh-14rem)]">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex items-start space-x-3.5 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {/* Profile Icons */}
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-caramel/10 border border-caramel/20 flex items-center justify-center text-caramel flex-shrink-0">
                  <Sparkles className="w-4 h-4" />
                </div>
              )}

              <div
                className={`p-4 text-xs leading-relaxed max-w-[85%] ${
                  msg.role === "user"
                    ? "chat-bubble-user text-silk"
                    : "chat-bubble-assistant text-silk-muted"
                }`}
              >
                {/* Message markdown or plain formatting */}
                <div className="whitespace-pre-wrap font-sans space-y-3">
                  {/* Quick helper for bold and bullets inside chat bubble */}
                  {msg.content.split("\n").map((line, idx) => {
                    if (line.startsWith("##")) {
                      return <h4 key={idx} className="font-bold text-silk text-sm pt-2">{line.replace(/##/g, "")}</h4>;
                    }
                    if (line.startsWith("-") || line.startsWith("*")) {
                      return <li key={idx} className="ml-4 list-disc">{line.substring(1).trim()}</li>;
                    }
                    return <p key={idx}>{line}</p>;
                  })}
                </div>

                {/* Citations section */}
                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-granite/10 space-y-2">
                    <span className="text-[10px] text-granite font-mono block uppercase tracking-wider">RETRIEVED CITATIONS:</span>
                    <div className="flex flex-wrap gap-2">
                      {msg.citations.map((cit, cidx) => (
                        <a
                          key={cidx}
                          href={cit.url || "#"}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-[9px] font-mono text-caramel-warm bg-caramel/5 px-2 py-0.5 rounded border border-caramel/10 hover:border-caramel transition-colors"
                          title={cit.title}
                        >
                          <LinkIcon className="w-2.5 h-2.5" />
                          <span>[{cidx + 1}] {cit.source}</span>
                        </a>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Loader bubble */}
          {loading && (
            <div className="flex items-start space-x-3.5 justify-start">
              <div className="w-8 h-8 rounded-full bg-caramel/10 border border-caramel/20 flex items-center justify-center text-caramel flex-shrink-0 animate-spin">
                <RefreshCw className="w-3.5 h-3.5" />
              </div>
              <div className="p-4 chat-bubble-assistant max-w-[85%] text-xs text-granite-light">
                <div className="flex items-center space-x-2">
                  <div className="typing-indicator flex items-center">
                    <span />
                    <span />
                    <span />
                  </div>
                  <span className="font-mono text-[10px] tracking-wider uppercase font-bold text-granite pl-2">RAG Search & Synthesis in progress...</span>
                </div>
              </div>
            </div>
          )}

          {/* Scroll Target */}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Questions Grid (Only show if history is short) */}
        {messages.length === 1 && !loading && (
          <div className="space-y-3">
            <h5 className="text-[10px] font-bold uppercase tracking-wider text-granite font-mono pl-1">Suggested inquiries</h5>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {suggestedQuestions.map((q, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSend(q)}
                  className="text-left text-xs bg-ash/40 border border-granite/10 rounded-lg p-3 hover:border-caramel/30 hover:bg-caramel/5 text-silk-muted hover:text-silk transition-all"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input Bar */}
        <div className="flex items-center space-x-3 pt-4 border-t border-granite/10 relative">
          {isDemo && (
            <div className="absolute bottom-full left-0 mb-2 text-[10px] text-caramel flex items-center space-x-1 pl-1">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Running in simulated Demo mode (LLM output generated from local fixtures)</span>
            </div>
          )}
          <Input
            placeholder="Search financial markets (e.g. 'What is driving NVIDIA sentiment?')"
            className="flex-1 h-11 text-xs"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleSend(input);
            }}
          />
          <Button
            onClick={() => handleSend(input)}
            disabled={!input.trim() || loading}
            size="icon"
            className="h-11 w-11 rounded-md"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </Shell>
  );
}
