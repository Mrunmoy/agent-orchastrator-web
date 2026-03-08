export type MessageType =
  | "chat_message"
  | "debate_turn"
  | "phase_change"
  | "system_notice"
  | "steer";

export interface ChatMessageData {
  id: string;
  agentName: string;
  agentId?: string;
  agentRole?: string;
  text: string;
  timestamp: string; // ISO-8601
  isUser: boolean;
  isThinking?: boolean;
  type?: MessageType;
  /** For debate_turn: current round number */
  round?: number;
  /** For debate_turn: total rounds */
  totalRounds?: number;
  /** For phase_change: the phase label */
  phaseLabel?: string;
}
