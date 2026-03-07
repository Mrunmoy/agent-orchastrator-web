export type RunStatus = "idle" | "running" | "paused" | "queued";

export interface SteeringEntry {
  id: string;
  text: string;
  timestamp: number;
}

export interface RunWindowProps {
  status: RunStatus;
  currentTurn: number;
  batchSize: number;
  elapsedSeconds: number;
  steeringHistory: SteeringEntry[];
  onNext20: () => void;
  onContinue20: () => void;
  onStopNow: () => void;
  onSteer: (note: string) => void;
}

export interface SteeringPanelProps {
  status: RunStatus;
  steeringHistory: SteeringEntry[];
  onSteer: (note: string) => void;
}
