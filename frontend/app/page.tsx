"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, Home as HomeIcon } from "lucide-react";
import AgentFeed, { FeedMessage } from "@/components/AgentFeed";
import ScoreCard, { ScorecardData } from "@/components/ScoreCard";

const CREW = [
  { name: "Brick",   role: "Real Estate Analyst",  bio: "Knows what homes actually cost and why.",              color: "#f59e0b" },
  { name: "Scholar", role: "Education Analyst",     bio: "Finds the real story behind school ratings.",          color: "#3b82f6" },
  { name: "Shield",  role: "Safety Analyst",        bio: "Presents safety data plainly. No alarm, no sugarcoating.", color: "#ef4444" },
  { name: "Vibe",    role: "Lifestyle Analyst",     bio: "Maps what makes a neighborhood actually livable.",   color: "#22c55e" },
  { name: "Gavel",   role: "Verdict Writer",        bio: "Weighs all inputs. Delivers a clear honest verdict.",  color: "#a855f7" },
];

const AGENT_ORDER = ["Brick", "Scholar", "Shield", "Vibe", "Gavel"];
const AGENT_ROLE_MAP: Record<string, string> = {
  "Real Estate Market Analyst": "Brick",
  "Education Research Analyst": "Scholar",
  "Safety and Crime Research Analyst": "Shield",
  "Neighborhood Lifestyle Analyst": "Vibe",
  "Neighborhood Evaluator": "Gavel",
};

function resolveAgentShortName(agent: string): string {
  return AGENT_ROLE_MAP[agent] || agent;
}

export default function Home() {
  const [location, setLocation] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [messages, setMessages] = useState<FeedMessage[]>([]);
  const [scorecard, setScorecard] = useState<ScorecardData | null>(null);
  const [activeLocation, setActiveLocation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const feedEndRef = useRef<HTMLDivElement>(null);

  const lastAgent = messages.length > 0 ? messages[messages.length - 1].agent : null;
  const activeAgentShort = lastAgent ? resolveAgentShortName(lastAgent) : null;

  useEffect(() => {
    if (feedEndRef.current) {
      feedEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!location.trim() || isStreaming) return;

    setMessages([]);
    setScorecard(null);
    setError(null);
    setIsStreaming(true);
    setActiveLocation(location.trim());

    try {
      const response = await fetch("/api/scout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ location: location.trim() }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === "step" || data.type === "system" || data.type === "task_complete") {
                setMessages((prev) => [...prev, data as FeedMessage]);
              } else if (data.type === "done") {
                if (data.error) setError(data.error);
                else setScorecard({ ...data.scorecard, raw: data.raw });
              }
            } catch {
              // skip malformed lines
            }
          }
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsStreaming(false);
    }
  }

  const completedAgents = new Set<string>();
  for (const msg of messages) {
    if (msg.type === "task_complete") {
      completedAgents.add(resolveAgentShortName(msg.agent));
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-16 space-y-12">
        {/* Hero */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.12 } } }}
          className="text-center space-y-4"
        >
          <motion.div
            variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
            className="flex justify-center"
          >
            <HomeIcon size={48} color="#c9a84c" />
          </motion.div>
          <motion.h1
            variants={{ hidden: { opacity: 0, y: 20 }, visible: { opacity: 1, y: 0 } }}
            className="font-display text-4xl md:text-5xl font-bold text-white leading-tight"
          >
            Know your neighborhood<br />before you buy.
          </motion.h1>
          <motion.p
            variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
            className="text-[#a0a0a0] text-lg"
          >
            Enter any city, neighborhood, or zip code.
          </motion.p>
          <motion.form
            variants={{ hidden: { opacity: 0, y: 16 }, visible: { opacity: 1, y: 0 } }}
            onSubmit={handleSubmit}
            className="flex gap-2 max-w-lg mx-auto"
          >
            <div className="relative flex-1">
              <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#a0a0a0]" />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Arcadia Phoenix AZ or 85018"
                className="w-full pl-9 pr-4 py-3 rounded-lg border border-[#2a2a2a] bg-[#1a1a1a] text-white placeholder-[#a0a0a0] focus:outline-none focus:ring-2 focus:ring-[#c9a84c]/40 text-sm"
                disabled={isStreaming}
              />
            </div>
            <button
              type="submit"
              disabled={!location.trim() || isStreaming}
              className="bg-[#c9a84c] text-[#0f0f0f] px-6 py-3 rounded-lg text-sm font-semibold hover:bg-[#e8d5a3] disabled:opacity-40 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
            >
              {isStreaming ? "Scouting…" : "Scout It"}
            </button>
          </motion.form>
        </motion.div>

        {/* Meet the Crew */}
        <div className="space-y-4">
          <h2 className="font-display text-xl font-semibold text-white">Meet the Crew</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {CREW.map((agent) => (
              <div
                key={agent.name}
                className="rounded-lg bg-[#1a1a1a] border border-[#2a2a2a] pl-3 pr-3 py-3 border-l-4"
                style={{ borderLeftColor: agent.color }}
              >
                <p className="font-semibold text-white text-sm">{agent.name}</p>
                <p className="text-xs text-[#a0a0a0] mt-0.5">{agent.role}</p>
                <p className="text-xs text-[#a0a0a0] mt-2 leading-snug">{agent.bio}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Agent progress bar */}
        <AnimatePresence>
          {isStreaming && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
            >
              <div className="flex gap-1 items-end">
                {AGENT_ORDER.map((agent) => {
                  const isActive = activeAgentShort === agent && isStreaming;
                  const isComplete = completedAgents.has(agent);
                  return (
                    <div key={agent} className="flex flex-col items-center gap-1 flex-1">
                      <div
                        className={`w-full h-1.5 rounded-full transition-all duration-500 ${
                          isComplete ? "bg-[#c9a84c]" : isActive ? "bg-[#e8d5a3] animate-pulse" : "bg-[#2a2a2a]"
                        }`}
                      />
                      <span
                        className={`text-xs font-mono ${
                          isComplete ? "text-[#c9a84c] font-semibold" : isActive ? "text-[#e8d5a3] font-semibold" : "text-[#a0a0a0]"
                        }`}
                      >
                        {isComplete ? "✓ " : ""}{agent}
                      </span>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Agent feed */}
        <AnimatePresence>
          {messages.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-3"
            >
              <h2 className="font-display text-lg font-semibold text-white">
                The crew is working&hellip;
              </h2>
              <AgentFeed messages={messages} isStreaming={isStreaming} feedEndRef={feedEndRef} />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-[#991b1b] bg-[#991b1b]/10 p-4 text-sm text-red-400">
            {error}
          </div>
        )}

        {/* Scorecard */}
        <AnimatePresence>
          {scorecard && (
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-4"
            >
              <h2 className="font-display text-2xl font-bold text-white">
                {activeLocation}
              </h2>
              <ScoreCard data={scorecard} location={activeLocation} />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <footer className="border-t border-[#2a2a2a] py-6 px-4">
        <div className="max-w-3xl mx-auto flex flex-col md:flex-row justify-between items-center gap-2 text-xs text-[#a0a0a0]">
          <span className="font-display font-semibold text-[#c9a84c]">HomeScout</span>
          <span>Know your neighborhood before you buy.</span>
          <span>© {new Date().getFullYear()} · Powered by CrewAI + Gemini</span>
        </div>
      </footer>
    </div>
  );
}
