import "./ChatPane.css";

export function ChatPane() {
  return (
    <main className="panel chat-pane" data-testid="chat-pane">
      <h3>Group Debate</h3>
      <div className="chat-pane__subbar">
        <span>No active conversation</span>
      </div>
      <div className="chat-pane__stream" data-testid="message-stream">
        <div className="chat-pane__empty">Select or create a conversation to begin.</div>
      </div>
      <div className="chat-pane__composer" data-testid="composer">
        <select>
          <option>Target First: All Agents</option>
        </select>
        <input type="text" placeholder="Type a message..." />
        <button className="btn btn--primary">Send To Group</button>
      </div>
    </main>
  );
}
