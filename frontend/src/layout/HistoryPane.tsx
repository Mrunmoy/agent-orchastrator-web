import "./HistoryPane.css";

export function HistoryPane() {
  return (
    <aside className="panel history-pane" data-testid="history-pane">
      <h3>Conversations</h3>
      <div className="history-pane__scroll">
        <div className="history-pane__actions">
          <button className="btn btn--primary">+ New</button>
          <button className="btn btn--subtle">Delete</button>
          <button className="btn btn--danger">Clear All</button>
        </div>

        <p className="section-title">Recent</p>
        <div className="conversation-list" data-testid="conversation-list">
          <div className="conv-row">
            <div className="conv-head">
              <span>No conversations yet</span>
            </div>
          </div>
        </div>

        <div className="agent-roster" data-testid="agent-roster">
          <p className="section-title">Agents In This Conversation</p>
          <div className="agent-roster__empty">No agents configured</div>
        </div>
      </div>
    </aside>
  );
}
