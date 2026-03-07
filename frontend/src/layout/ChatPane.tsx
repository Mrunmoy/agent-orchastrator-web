import { useState } from "react";
import "./ChatPane.css";

export type ChatMessage = {
  id: string;
  sender: string;
  text: string;
  timestamp: string;
};

type ChatPaneProps = {
  activeConversationTitle?: string | null;
  messages?: ChatMessage[];
  onSend?: (text: string, target: string) => void;
};

export function ChatPane({ activeConversationTitle = null, messages = [], onSend }: ChatPaneProps) {
  const [text, setText] = useState("");
  const [target, setTarget] = useState("all");

  const send = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSend?.(trimmed, target);
    setText("");
  };

  return (
    <main className="panel chat-pane" data-testid="chat-pane">
      <h3>Group Debate</h3>
      <div className="chat-pane__subbar">
        <span>{activeConversationTitle ?? "No active conversation"}</span>
      </div>
      <div className="chat-pane__stream" data-testid="message-stream">
        {messages.length === 0 ? (
          <div className="chat-pane__empty">Select or create a conversation to begin.</div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className="chat-message">
              <strong>{message.sender}</strong> <span>{message.text}</span>
            </div>
          ))
        )}
      </div>
      <div className="chat-pane__composer" data-testid="composer">
        <select value={target} onChange={(event) => setTarget(event.target.value)}>
          <option value="all">Target First: All Agents</option>
          <option value="codex">Target First: Codex</option>
          <option value="claude">Target First: Claude</option>
        </select>
        <input
          type="text"
          value={text}
          onChange={(event) => setText(event.target.value)}
          placeholder="Type a message..."
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              send();
            }
          }}
        />
        <button className="btn btn--primary" onClick={send}>
          Send To Group
        </button>
      </div>
    </main>
  );
}
