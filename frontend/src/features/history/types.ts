export type ConversationState =
  | "queued"
  | "debate"
  | "execution_planning"
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
