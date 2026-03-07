export type AgreementLevel =
  | "strong_agree"
  | "agree"
  | "neutral"
  | "disagree"
  | "strong_disagree";

export interface AgentPosition {
  agent_id: string;
  agent_name: string;
  position: AgreementLevel;
  summary: string;
}

export interface NeutralMemo {
  generated_at: string;
  summary: string;
  key_points: string[];
  recommendation: string;
}

export interface IntelligenceData {
  conversation_id: string;
  positions: AgentPosition[];
  memo: NeutralMemo | null;
}
