import { motion } from "framer-motion";
import "./HistoryPane.css";
import { AgentRoster } from "../features/agents";
import type { AgentData } from "../features/agents/types";
import { staggerContainer, slideInLeft } from "../utils/animations";

export type ConversationSummary = {
  id: string;
  title: string;
  updatedAt: string;
};

type HistoryPaneProps = {
  conversations?: ConversationSummary[];
  selectedConversationId?: string | null;
  agents?: AgentData[];
  onNewConversation?: () => void;
  onDeleteConversation?: () => void;
  onClearConversations?: () => void;
  onSelectConversation?: (conversationId: string) => void;
  onAddAgent?: () => void;
  onEditAgent?: (agentId: string) => void;
  reorderConversationAgents?: (agentIds: string[]) => Promise<unknown>;
};

export function HistoryPane({
  conversations = [],
  selectedConversationId = null,
  agents = [],
  onNewConversation,
  onDeleteConversation,
  onClearConversations,
  onSelectConversation,
  onAddAgent,
  onEditAgent,
  reorderConversationAgents,
}: HistoryPaneProps) {
  return (
    <aside className="panel history-pane" data-testid="history-pane">
      <h3>Conversations</h3>
      <div className="history-pane__scroll">
        <div className="history-pane__actions">
          <button className="btn btn--primary" onClick={onNewConversation}>
            + New
          </button>
          <button className="btn btn--subtle" onClick={onDeleteConversation}>
            Delete
          </button>
          <button className="btn btn--danger" onClick={onClearConversations}>
            Clear All
          </button>
        </div>

        <p className="section-title">Recent</p>
        <motion.div
          className="conversation-list"
          data-testid="conversation-list"
          variants={staggerContainer}
          initial="initial"
          animate="animate"
        >
          {conversations.length === 0 ? (
            <div className="conv-row">
              <div className="conv-head">
                <span>No conversations yet</span>
              </div>
            </div>
          ) : (
            conversations.map((conversation) => (
              <motion.button
                key={conversation.id}
                className="conv-row"
                data-selected={conversation.id === selectedConversationId}
                onClick={() => onSelectConversation?.(conversation.id)}
                variants={slideInLeft}
              >
                <div className="conv-head">
                  <span>{conversation.title}</span>
                </div>
                <small>{new Date(conversation.updatedAt).toLocaleTimeString()}</small>
              </motion.button>
            ))
          )}
        </motion.div>

        <AgentRoster
          agents={agents}
          onAdd={() => onAddAgent?.()}
          onEdit={(agentId) => onEditAgent?.(agentId)}
          reorderConversationAgents={reorderConversationAgents}
        />
      </div>
    </aside>
  );
}
