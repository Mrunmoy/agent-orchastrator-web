/** The six workflow phases in the debate-to-agreement pipeline. */
export type DebatePhase =
  | "Design Debate"
  | "TDD Planning"
  | "Implementation"
  | "Integration"
  | "Docs"
  | "Merge";

/** Props for the PhaseBanner component. */
export interface PhaseBannerProps {
  /** Current phase label. */
  phase: DebatePhase | string;
  /** Current round number (1-based). */
  round: number;
  /** Total rounds in this phase. */
  totalRounds: number;
  /** Name of the agent currently generating, or null if idle. */
  speakingAgent?: string | null;
}
