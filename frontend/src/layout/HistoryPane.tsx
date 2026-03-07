import "./HistoryPane.css";

export type ConversationSummary = {
  id: string;
  title: string;
  updatedAt: string;
};

type HistoryPaneProps = {
  conversations?: ConversationSummary[];
  selectedConversationId?: string | null;
  onNewConversation?: () => void;
  onDeleteConversation?: () => void;
  onClearConversations?: () => void;
  onSelectConversation?: (conversationId: string) => void;
};

export function HistoryPane({
  conversations = [],
  selectedConversationId = null,
  onNewConversation,
  onDeleteConversation,
  onClearConversations,
  onSelectConversation,
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
        <div className="conversation-list" data-testid="conversation-list">
          {conversations.length === 0 ? (
            <div className="conv-row">
              <div className="conv-head">
                <span>No conversations yet</span>
              </div>
            </div>
          ) : (
            conversations.map((conversation) => (
              <button
                key={conversation.id}
                className="conv-row"
                data-selected={conversation.id === selectedConversationId}
                onClick={() => onSelectConversation?.(conversation.id)}
              >
                <div className="conv-head">
                  <span>{conversation.title}</span>
                </div>
                <small>{new Date(conversation.updatedAt).toLocaleTimeString()}</small>
              </button>
            ))
          )}
        </div>

        <div className="agent-roster" data-testid="agent-roster">
          <p className="section-title">Agents In This Conversation</p>
          <div className="agent-roster__empty">No agents configured</div>
        </div>
      </div>
    </aside>
  );
}
