"use client";

import { RefObject } from "react";

export interface FeedMessage {
  type: string;
  agent: string;
  message: string;
}

interface AgentFeedProps {
  messages: FeedMessage[];
  isStreaming: boolean;
  feedEndRef: RefObject<HTMLDivElement | null>;
}

const AGENT_STYLES: Record<
  string,
  { border: string; text: string; bg: string; badge: string }
> = {
  Brick: {
    border: "border-[#f59e0b]",
    text: "text-[#f59e0b]",
    bg: "bg-[#1a1a1a]",
    badge: "BRICK",
  },
  Scholar: {
    border: "border-[#3b82f6]",
    text: "text-[#3b82f6]",
    bg: "bg-[#1a1a1a]",
    badge: "SCHOLAR",
  },
  Shield: {
    border: "border-[#ef4444]",
    text: "text-[#ef4444]",
    bg: "bg-[#1a1a1a]",
    badge: "SHIELD",
  },
  Vibe: {
    border: "border-[#22c55e]",
    text: "text-[#22c55e]",
    bg: "bg-[#1a1a1a]",
    badge: "VIBE",
  },
  Gavel: {
    border: "border-[#a855f7]",
    text: "text-[#a855f7]",
    bg: "bg-[#1a1a1a]",
    badge: "GAVEL",
  },
  System: {
    border: "border-[#6b7280]",
    text: "text-[#6b7280]",
    bg: "bg-[#1a1a1a]",
    badge: "SYSTEM",
  },
};

// Map full agent names (from crew definitions) to short names
const AGENT_NAME_MAP: Record<string, string> = {
  "Real Estate Market Analyst": "Brick",
  "Education Research Analyst": "Scholar",
  "Safety and Crime Research Analyst": "Shield",
  "Neighborhood Lifestyle Analyst": "Vibe",
  "Neighborhood Evaluator": "Gavel",
};

function getAgentStyle(agent: string) {
  const shortName = AGENT_NAME_MAP[agent] || agent;
  return (
    AGENT_STYLES[shortName] || {
      border: "border-[#6b7280]",
      text: "text-[#6b7280]",
      bg: "bg-[#1a1a1a]",
      badge: agent.toUpperCase().slice(0, 8),
    }
  );
}

export default function AgentFeed({
  messages,
  isStreaming,
  feedEndRef,
}: AgentFeedProps) {
  return (
    <div className="relative rounded-lg overflow-hidden border border-[#2a2a2a] bg-[#0f0f0f]">
      {/* Header bar */}
      <div className="flex items-center gap-2 px-4 py-2 bg-[#1a1a1a] border-b border-[#2a2a2a]">
        <span className="text-xs font-mono text-[#a0a0a0] uppercase tracking-widest">
          Agent Feed
        </span>
        {isStreaming && (
          <span className="ml-auto flex items-center gap-1.5">
            <span className="inline-block h-2 w-2 rounded-full bg-[#c9a84c] animate-pulse" />
            <span className="text-xs font-mono text-[#c9a84c]">live</span>
          </span>
        )}
      </div>

      {/* Messages */}
      <div className="h-96 overflow-y-auto p-4 space-y-3 font-mono text-sm">
        {messages.length === 0 && (
          <p className="text-[#a0a0a0] text-xs">Waiting for crew to start...</p>
        )}
        {messages.map((msg, i) => {
          const style = getAgentStyle(msg.agent);
          return (
            <div
              key={i}
              className={`rounded border-l-2 px-3 py-2 ${style.border} ${style.bg}`}
            >
              <span
                className={`text-xs font-bold uppercase tracking-widest ${style.text}`}
              >
                {style.badge}
              </span>
              <p className="mt-1 text-[#a0a0a0] text-xs leading-relaxed whitespace-pre-wrap break-words">
                {msg.message}
              </p>
            </div>
          );
        })}
        <div ref={feedEndRef} />
      </div>
    </div>
  );
}
