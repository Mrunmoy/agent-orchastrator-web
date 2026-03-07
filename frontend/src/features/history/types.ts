export type ConversationState =
  | "debate"
  | "autonomous_work"
  | "needs_user_input"
  | "completed"
  | "failed";

export interface ConversationSummary {
  id: string;
  title: string;
  state: ConversationState;
  active: boolean;
  updated_at: string;
}
