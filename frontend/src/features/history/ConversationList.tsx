import React from "react";
import { ConversationItem } from "./ConversationItem";
import type { ConversationSummary } from "./types";
import "./ConversationList.css";

export interface ConversationListProps {
  conversations: ConversationSummary[];
  onSelect: (id: string) => void;
  onCreate: () => void;
  onClearAll: () => void;
}

export function ConversationList({
  conversations,
  onSelect,
  onCreate,
  onClearAll,
}: ConversationListProps) {
  const handleClearAll = () => {
    if (window.confirm("Clear all conversations? This cannot be undone.")) {
      onClearAll();
    }
  };

  return (
    <div className="conversation-list-container" data-testid="conversation-list-container">
      <div className="conversation-list__actions">
        <button
          className="btn btn--primary"
          onClick={onCreate}
          type="button"
        >
          + New Conversation
        </button>
        <button
          className="btn btn--danger"
          onClick={handleClearAll}
          type="button"
        >
          Clear All
        </button>
      </div>

      <div className="conversation-list__items">
        {conversations.length === 0 ? (
          <p className="conversation-list__empty">No conversations yet</p>
        ) : (
          conversations.map((conv) => (
            <ConversationItem
              key={conv.id}
              conversation={conv}
              onSelect={onSelect}
            />
          ))
        )}
      </div>
    </div>
  );
}
