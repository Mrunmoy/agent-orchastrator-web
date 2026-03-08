import { useState } from "react";
import type { ChatMessageData } from "../features/chat/types";
import { ChatTimeline } from "../features/chat/ChatTimeline";
import "./ChatPane.css";

type ChatPaneProps = {
  activeConversationTitle?: string | null;
  messages?: ChatMessageData[];
  onSend?: (text: string) => void;
};

export function ChatPane({
  activeConversationTitle = null,
  messages = [],
  onSend,
}: ChatPaneProps) {
  const [text, setText] = useState("");

  const send = () => {
    const trimmed = text.trim();
    if (!trimmed) return;
    onSend?.(trimmed);
    setText("");
  };

  return (
    <main className="panel chat-pane" data-testid="chat-pane">
      <h3>Group Debate</h3>
      <div className="chat-pane__subbar">
        <span>{activeConversationTitle ?? "No active conversation"}</span>
      </div>
      <ChatTimeline messages={messages} />
      <div className="chat-pane__composer" data-testid="composer">
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
