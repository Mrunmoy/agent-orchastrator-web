export interface ChatMessageData {
  id: string;
  agentName: string;
  text: string;
  timestamp: string; // ISO-8601
  isUser: boolean;
  isThinking?: boolean;
}
