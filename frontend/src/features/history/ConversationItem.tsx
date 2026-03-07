import React from "react";
import type { ConversationSummary } from "./types";
import "./ConversationItem.css";

const MAX_TITLE_LENGTH = 50;

function truncateTitle(title: string): string {
  if (title.length <= MAX_TITLE_LENGTH) return title;
  return title.slice(0, MAX_TITLE_LENGTH - 3) + "...";
}

function relativeTime(isoDate: string): string {
  const now = Date.now();
  const then = new Date(isoDate).getTime();
  const diffMs = now - then;
  const diffSec = Math.floor(diffMs / 1000);

  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  return `${diffDay}d ago`;
}

export interface ConversationItemProps {
  conversation: ConversationSummary;
  onSelect: (id: string) => void;
}

export function ConversationItem({ conversation, onSelect }: ConversationItemProps) {
  const { id, title, state, active, updated_at } = conversation;
  const classes = ["conv-item", active ? "conv-item--active" : ""].filter(Boolean).join(" ");

  return (
    <div
      className={classes}
      data-testid="conv-item"
      onClick={() => onSelect(id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") onSelect(id);
      }}
    >
      <span className="conv-item__title" data-testid="conv-item-title">
        {truncateTitle(title)}
      </span>
      <span className={`conv-item__badge badge--${state}`} data-testid="state-badge">
        {state}
      </span>
      <span className="conv-item__time" data-testid="conv-item-time">
        {relativeTime(updated_at)}
      </span>
    </div>
  );
}
