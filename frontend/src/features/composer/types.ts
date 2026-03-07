export interface ComposerProps {
  agents: { id: string; display_name: string }[];
  onSend: (message: string) => void;
  disabled?: boolean;
}

export interface RunControlsProps {
  status: "idle" | "running" | "paused" | "queued";
  onRun: () => void;
  onContinue: () => void;
  onStop: () => void;
  onSteer: (note: string) => void;
}
