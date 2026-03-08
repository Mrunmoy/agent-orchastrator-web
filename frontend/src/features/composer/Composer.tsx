import type React from "react";
import { useState, useRef, useCallback } from "react";
import type { ComposerProps, ComposerAgent } from "./types";
import "./Composer.css";

/**
 * Extract the @mention query from the text at the given cursor position.
 * Returns the query string (after @) or null if no active mention.
 */
function getMentionQuery(text: string, cursorPos: number): string | null {
  // Walk backwards from cursor to find '@'
  const beforeCursor = text.slice(0, cursorPos);
  const atIndex = beforeCursor.lastIndexOf("@");
  if (atIndex === -1) return null;

  // '@' must be at start of text or preceded by whitespace
  if (atIndex > 0 && !/\s/.test(beforeCursor[atIndex - 1] ?? "")) return null;

  const query = beforeCursor.slice(atIndex + 1);
  // If there's a space in the query, the mention is complete
  if (/\s/.test(query)) return null;

  return query;
}

/**
 * Parse the first @mention from message text and resolve to an agent ID.
 */
function resolveTargetAgent(
  text: string,
  agents: ComposerAgent[],
): string | undefined {
  const mentionRegex = /@(\S+)/;
  const match = mentionRegex.exec(text);
  if (!match) return undefined;

  const mentionName = match[1] ?? "";
  const agent = agents.find(
    (a) => a.display_name.toLowerCase() === mentionName.toLowerCase(),
  );
  return agent?.id;
}

export function Composer({
  onSend,
  disabled = false,
  agents = [],
}: Omit<ComposerProps, "agents"> & { agents?: ComposerProps["agents"] }) {
  const [message, setMessage] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredAgents, setFilteredAgents] = useState<ComposerAgent[]>([]);
  const [highlightIndex, setHighlightIndex] = useState(0);
  const [mentionStart, setMentionStart] = useState<number | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const updateMentionState = useCallback(
    (text: string, cursorPos: number) => {
      const query = getMentionQuery(text, cursorPos);
      if (query !== null) {
        const filtered = agents.filter((a) =>
          a.display_name.toLowerCase().startsWith(query.toLowerCase()),
        );
        if (filtered.length > 0) {
          setFilteredAgents(filtered);
          setShowDropdown(true);
          setHighlightIndex(0);
          // Find where the @ is
          const beforeCursor = text.slice(0, cursorPos);
          const atIndex = beforeCursor.lastIndexOf("@");
          setMentionStart(atIndex);
        } else {
          setShowDropdown(false);
          setFilteredAgents([]);
        }
      } else {
        setShowDropdown(false);
        setFilteredAgents([]);
      }
    },
    [agents],
  );

  function handleChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    const newValue = e.target.value;
    setMessage(newValue);
    const cursorPos = e.target.selectionStart ?? newValue.length;
    updateMentionState(newValue, cursorPos);
    autoResize(e.target);
  }

  function selectAgent(agent: ComposerAgent) {
    if (mentionStart === null) return;
    const cursorPos = textareaRef.current?.selectionStart ?? message.length;
    const before = message.slice(0, mentionStart);
    const after = message.slice(cursorPos);
    const newMessage = `${before}@${agent.display_name} ${after}`;
    setMessage(newMessage);
    setShowDropdown(false);
    setFilteredAgents([]);
    setMentionStart(null);

    // Focus back on textarea
    requestAnimationFrame(() => {
      if (textareaRef.current) {
        const newCursorPos = mentionStart + agent.display_name.length + 2; // @name + space
        textareaRef.current.focus();
        textareaRef.current.selectionStart = newCursorPos;
        textareaRef.current.selectionEnd = newCursorPos;
      }
    });
  }

  function handleSend() {
    const trimmed = message.trim();
    if (!trimmed) return;
    const targetAgentId = resolveTargetAgent(trimmed, agents);
    onSend(trimmed, targetAgentId);
    setMessage("");
    setShowDropdown(false);
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (showDropdown) {
      if (e.key === "ArrowDown") {
        e.preventDefault();
        setHighlightIndex((prev) =>
          prev < filteredAgents.length - 1 ? prev + 1 : prev,
        );
        return;
      }
      if (e.key === "ArrowUp") {
        e.preventDefault();
        setHighlightIndex((prev) => (prev > 0 ? prev - 1 : prev));
        return;
      }
      if (e.key === "Enter") {
        e.preventDefault();
        const selected = filteredAgents[highlightIndex];
        if (selected) selectAgent(selected);
        return;
      }
      if (e.key === "Escape") {
        e.preventDefault();
        setShowDropdown(false);
        return;
      }
    }

    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function autoResize(textarea: HTMLTextAreaElement) {
    textarea.style.height = "auto";
    const lineHeight = 20; // approx line height in px
    const maxHeight = lineHeight * 6;
    textarea.style.height = `${Math.min(textarea.scrollHeight, maxHeight)}px`;
  }

  return (
    <div className="composer" data-testid="composer">
      <div className="composer__input-row">
        <div className="composer__input-wrapper">
          <textarea
            ref={textareaRef}
            className="composer__input"
            data-testid="composer-input"
            placeholder="Type a message... Use @ to mention an agent"
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            rows={1}
          />
          {showDropdown && (
            <ul
              className="composer__mention-dropdown"
              data-testid="mention-dropdown"
              role="listbox"
            >
              {filteredAgents.map((agent, index) => (
                <li
                  key={agent.id}
                  className={`composer__mention-option${index === highlightIndex ? " composer__mention-option--active" : ""}`}
                  role="option"
                  aria-selected={index === highlightIndex}
                  onMouseDown={(e) => {
                    e.preventDefault(); // Prevent blur
                    selectAgent(agent);
                  }}
                >
                  {agent.display_name}
                </li>
              ))}
            </ul>
          )}
        </div>
        <button
          className="composer__send-button"
          data-testid="send-button"
          onClick={handleSend}
          disabled={disabled}
          type="button"
        >
          Send
        </button>
      </div>
    </div>
  );
}
