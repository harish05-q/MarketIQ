import * as React from "react";
import { cn } from "@/lib/utils";

// --- Badge Component ---
export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "outline" | "positive" | "negative" | "neutral" | "warning";
}

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold font-mono transition-colors",
        {
          "bg-caramel text-ash-deep": variant === "default",
          "bg-ash-light text-silk-muted": variant === "secondary",
          "border border-granite text-silk-muted": variant === "outline",
          "sentiment-positive": variant === "positive",
          "sentiment-negative": variant === "negative",
          "sentiment-neutral": variant === "neutral",
          "bg-warning/20 text-warning border border-warning/30": variant === "warning",
        },
        className
      )}
      {...props}
    />
  );
}

// --- Button Component ---
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "secondary" | "outline" | "ghost" | "link";
  size?: "default" | "sm" | "lg" | "icon";
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        className={cn(
          "inline-flex items-center justify-center rounded-md text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-caramel disabled:pointer-events-none disabled:opacity-50 active:scale-[0.98]",
          {
            "btn-primary": variant === "default",
            "bg-ash-light text-silk hover:bg-ash-light/80 border border-granite/20": variant === "secondary",
            "border border-granite/40 bg-transparent text-silk hover:bg-ash/50 hover:border-caramel/40": variant === "outline",
            "btn-ghost": variant === "ghost",
            "text-caramel underline-offset-4 hover:underline bg-transparent": variant === "link",
          },
          {
            "h-9 px-4 py-2": size === "default",
            "h-8 rounded-md px-3 text-xs": size === "sm",
            "h-10 rounded-md px-8": size === "lg",
            "h-9 w-9 p-0": size === "icon",
          },
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

// --- Card Component ---
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: boolean;
}

export function Card({ className, glass = true, ...props }: CardProps) {
  return (
    <div
      className={cn(
        glass ? "glass-card" : "glass-card-static",
        "relative overflow-hidden",
        className
      )}
      {...props}
    />
  );
}

export function CardHeader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex flex-col space-y-1.5 p-6", className)} {...props} />;
}

export function CardTitle({ className, ...props }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3
      className={cn("text-lg font-semibold leading-none tracking-tight text-silk", className)}
      {...props}
    />
  );
}

export function CardDescription({ className, ...props }: React.HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn("text-xs text-granite-light font-medium", className)} {...props} />;
}

export function CardContent({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("p-6 pt-0", className)} {...props} />;
}

export function CardFooter({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("flex items-center p-6 pt-0 border-t border-granite/10 mt-4", className)} {...props} />;
}

// --- Input Component ---
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-9 w-full rounded-md border border-granite/20 bg-ash/40 px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-granite-light focus-visible:outline-none focus-visible:border-caramel/60 disabled:cursor-not-allowed disabled:opacity-50 text-silk",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

// --- Tabs Components ---
interface TabsContextType {
  value: string;
  onValueChange: (value: string) => void;
}

const TabsContext = React.createContext<TabsContextType | undefined>(undefined);

export interface TabsProps extends React.HTMLAttributes<HTMLDivElement> {
  defaultValue: string;
  value?: string;
  onValueChange?: (value: string) => void;
}

export function Tabs({ defaultValue, value, onValueChange, children, className, ...props }: TabsProps) {
  const [activeTab, setActiveTab] = React.useState(defaultValue);
  const val = value !== undefined ? value : activeTab;
  const setVal = onValueChange || setActiveTab;

  return (
    <TabsContext.Provider value={{ value: val, onValueChange: setVal }}>
      <div className={cn("w-full", className)} {...props}>
        {children}
      </div>
    </TabsContext.Provider>
  );
}

export function TabsList({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "inline-flex h-9 items-center justify-center rounded-lg bg-ash-deep/60 p-1 border border-granite/10 text-granite-light",
        className
      )}
      {...props}
    />
  );
}

export interface TabsTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  value: string;
}

export function TabsTrigger({ value, className, children, ...props }: TabsTriggerProps) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error("TabsTrigger must be used inside Tabs");

  const isActive = context.value === value;

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-xs font-semibold transition-all focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50",
        isActive
          ? "bg-caramel text-ash-deep shadow"
          : "hover:text-silk hover:bg-ash/30",
        className
      )}
      onClick={() => context.onValueChange(value)}
      {...props}
    >
      {children}
    </button>
  );
}

export interface TabsContentProps extends React.HTMLAttributes<HTMLDivElement> {
  value: string;
}

export function TabsContent({ value, className, children, ...props }: TabsContentProps) {
  const context = React.useContext(TabsContext);
  if (!context) throw new Error("TabsContent must be used inside Tabs");

  if (context.value !== value) return null;

  return (
    <div
      className={cn(
        "mt-2 focus-visible:outline-none animate-fade-in",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

// --- Tooltip Component (Simple Title-based fallback) ---
export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactElement;
  className?: string;
}

export function Tooltip({ content, children, className }: TooltipProps) {
  return (
    <div className={cn("group relative inline-block", className)}>
      {children}
      <div className="pointer-events-none absolute bottom-full left-1/2 z-50 mb-2 -translate-x-1/2 whitespace-nowrap rounded bg-ash-deep border border-granite/20 px-2 py-1 text-xs text-silk opacity-0 transition-opacity group-hover:opacity-100 shadow-xl">
        {content}
      </div>
    </div>
  );
}
