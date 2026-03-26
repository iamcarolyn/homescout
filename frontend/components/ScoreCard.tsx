"use client";

import { motion } from "framer-motion";
import { Download } from "lucide-react";

interface ScoreField {
  score: number;
  rationale: string;
}

export interface ScorecardData {
  price_score?: ScoreField;
  school_score?: ScoreField;
  safety_score?: ScoreField;
  lifestyle_score?: ScoreField;
  overall_verdict?: string;
  key_strengths?: string[];
  key_concerns?: string[];
  summary?: string;
  raw?: string;
}

interface ScoreCardProps {
  data: ScorecardData;
  location: string;
}

function scoreColor(score?: number): string {
  if (!score) return "bg-[#1a1a1a] text-[#a0a0a0] border-[#2a2a2a]";
  if (score >= 8) return "bg-[#c9a84c] text-[#0f0f0f] border-[#c9a84c]";
  if (score >= 6) return "bg-[#d97706] text-white border-[#d97706]";
  if (score >= 4) return "bg-[#c2410c] text-white border-[#c2410c]";
  return "bg-[#991b1b] text-white border-[#991b1b]";
}

function verdictColor(verdict?: string): string {
  if (!verdict) return "bg-[#1a1a1a] border-[#2a2a2a]";
  const v = verdict.toLowerCase();
  if (v.includes("strong buy")) return "bg-[#c9a84c]/10 border-[#c9a84c]";
  if (v.includes("consider")) return "bg-[#d97706]/10 border-[#d97706]";
  if (v.includes("caution")) return "bg-[#c2410c]/10 border-[#c2410c]";
  if (v.includes("pass")) return "bg-[#991b1b]/10 border-[#991b1b]";
  return "bg-[#1a1a1a] border-[#2a2a2a]";
}

const SCORE_LABELS = [
  { key: "price_score" as const, label: "Price" },
  { key: "school_score" as const, label: "Schools" },
  { key: "safety_score" as const, label: "Safety" },
  { key: "lifestyle_score" as const, label: "Lifestyle" },
];

export default function ScoreCard({ data, location }: ScoreCardProps) {
  function handleDownload() {
    const raw = data.raw || JSON.stringify(data, null, 2);
    const blob = new Blob(
      [`# HomeScout Scorecard — ${location}\n\n${raw}`],
      { type: "text/markdown" }
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `homescout-${location.toLowerCase().replace(/\s+/g, "-")}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="space-y-6"
    >
      {/* Score grid */}
      <div className="grid grid-cols-2 gap-4">
        {SCORE_LABELS.map(({ key, label }) => {
          const field = data[key];
          return (
            <div
              key={key}
              className={`rounded-lg border p-4 ${scoreColor(field?.score)}`}
            >
              <div className="flex items-baseline justify-between">
                <span className="text-sm font-semibold uppercase tracking-wide opacity-90">
                  {label}
                </span>
                <span className="text-2xl font-bold">
                  {field?.score ?? "—"}/10
                </span>
              </div>
              {field?.rationale && (
                <p className="mt-1 text-xs opacity-80 leading-snug">
                  {field.rationale}
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Verdict */}
      {data.overall_verdict && (
        <div
          className={`rounded-lg border-2 px-5 py-4 ${verdictColor(data.overall_verdict)}`}
        >
          <p className="text-xs font-bold uppercase tracking-widest text-[#a0a0a0] mb-1">
            Overall Verdict
          </p>
          <p className="text-xl font-bold text-white">
            {data.overall_verdict}
          </p>
        </div>
      )}

      {/* Strengths and Concerns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.key_strengths && data.key_strengths.length > 0 && (
          <div className="rounded-lg border border-[#2a2a2a] bg-[#1a1a1a] p-4">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[#c9a84c] mb-2">
              Key Strengths
            </h4>
            <ul className="space-y-1">
              {data.key_strengths.map((s, i) => (
                <li key={i} className="flex gap-2 text-sm text-[#a0a0a0]">
                  <span className="text-[#c9a84c] font-bold mt-0.5">+</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {data.key_concerns && data.key_concerns.length > 0 && (
          <div className="rounded-lg border border-[#2a2a2a] bg-[#1a1a1a] p-4">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[#991b1b] mb-2">
              Key Concerns
            </h4>
            <ul className="space-y-1">
              {data.key_concerns.map((c, i) => (
                <li key={i} className="flex gap-2 text-sm text-[#a0a0a0]">
                  <span className="text-red-500 font-bold mt-0.5">−</span>
                  <span>{c}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Summary */}
      {data.summary && (
        <div className="rounded-lg border border-[#2a2a2a] bg-[#1a1a1a] p-4">
          <h4 className="text-xs font-bold uppercase tracking-widest text-[#a0a0a0] mb-2">
            Summary
          </h4>
          <p className="text-sm text-[#a0a0a0] leading-relaxed">
            {data.summary}
          </p>
        </div>
      )}

      {/* Download */}
      <button
        onClick={handleDownload}
        className="flex items-center gap-2 text-sm font-medium text-[#c9a84c] border border-[#c9a84c] rounded-lg px-4 py-2 hover:bg-[#c9a84c] hover:text-[#0f0f0f] transition-colors"
      >
        <Download size={14} />
        Download scorecard
      </button>
    </motion.div>
  );
}
