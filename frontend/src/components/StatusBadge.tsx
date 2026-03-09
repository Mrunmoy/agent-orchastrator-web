import {
  CircleDashed,
  Lightning,
  Warning,
  CheckCircle,
  XCircle,
  WifiSlash,
  Queue,
  Pause,
} from "@phosphor-icons/react";
import type { ComponentType } from "react";
import "./StatusBadge.css";

export type BadgeStatus =
  | "idle"
  | "running"
  | "blocked"
  | "done"
  | "failed"
  | "offline"
  | "queued"
  | "paused";

type BadgeSize = "sm" | "md";

type StatusBadgeProps = {
  status: BadgeStatus;
  size?: BadgeSize;
};

const iconMap: Record<BadgeStatus, ComponentType<{ size: number }>> = {
  idle: CircleDashed,
  running: Lightning,
  blocked: Warning,
  done: CheckCircle,
  failed: XCircle,
  offline: WifiSlash,
  queued: Queue,
  paused: Pause,
};

const iconSize: Record<BadgeSize, number> = {
  sm: 12,
  md: 14,
};

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  const Icon = iconMap[status];
  const className = `status-badge${size === "sm" ? " status-badge--sm" : ""}`;

  return (
    <span
      className={className}
      data-testid="status-badge"
      data-status={status}
    >
      <span className="status-badge__icon">
        <Icon size={iconSize[size]} />
      </span>
      {status}
    </span>
  );
}
