import React from "react";
import type { AgentPosition, AgreementLevel } from "./types";
import "./AgreementBar.css";

interface AgreementBarProps {
  positions: AgentPosition[];
}

const LEVEL_ORDER: AgreementLevel[] = [
  "strong_agree",
  "agree",
  "neutral",
  "disagree",
  "strong_disagree",
];

interface GroupedSegment {
  level: AgreementLevel;
  agents: AgentPosition[];
}

function groupByLevel(positions: AgentPosition[]): GroupedSegment[] {
  const groups = new Map<AgreementLevel, AgentPosition[]>();
  for (const pos of positions) {
    const existing = groups.get(pos.position) || [];
    existing.push(pos);
    groups.set(pos.position, existing);
  }

  return LEVEL_ORDER.filter((level) => groups.has(level)).map((level) => ({
    level,
    agents: groups.get(level)!,
  }));
}

export const AgreementBar: React.FC<AgreementBarProps> = ({ positions }) => {
  const segments = groupByLevel(positions);
  const total = positions.length;

  return (
    <div className="agreement-bar" data-testid="agreement-bar">
      {segments.map((seg) => {
        const widthPercent = total > 0 ? (seg.agents.length / total) * 100 : 0;
        const names = seg.agents.map((a) => a.agent_name).join(", ");
        return (
          <div
            key={seg.level}
            className={`agreement-segment segment-${seg.level}`}
            style={{ width: `${widthPercent}%` }}
            title={names}
          >
            {seg.agents.length}
          </div>
        );
      })}
    </div>
  );
};
