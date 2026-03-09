import type { ReactNode } from "react";
import "./StatsCard.css";

type StatsCardProps = {
  label: string;
  value: number | string;
  icon?: ReactNode;
  color?: string;
};

function slugify(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}

export function StatsCard({ label, value, icon, color }: StatsCardProps) {
  return (
    <div
      className="stats-card"
      data-testid={`stats-card-${slugify(label)}`}
      style={color ? { borderTopColor: color } : undefined}
    >
      {icon && <div className="stats-card__icon">{icon}</div>}
      <div className="stats-card__value">{value}</div>
      <div className="stats-card__label">{label}</div>
    </div>
  );
}
