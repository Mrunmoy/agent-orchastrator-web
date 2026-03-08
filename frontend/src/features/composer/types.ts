export interface ComposerAgent {
  id: string;
  display_name: string;
}

export interface ComposerProps {
  agents: ComposerAgent[];
  onSend: (message: string, targetAgentId?: string) => void;
  disabled?: boolean;
}

export interface RunControlsProps {
  status: "idle" | "running" | "paused" | "queued";
  onRun: () => void;
  onContinue: () => void;
  onStop: () => void;
  onSteer: (note: string) => void;
}
