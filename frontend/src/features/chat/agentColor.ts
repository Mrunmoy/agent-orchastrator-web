/**
 * Deterministic HSL hue from an agent ID string.
 * Uses a simple hash (djb2) mapped to 0-359.
 */
export function agentHue(agentId: string): number {
  let hash = 5381;
  for (let i = 0; i < agentId.length; i++) {
    hash = (hash * 33) ^ agentId.charCodeAt(i);
  }
  return ((hash >>> 0) % 360);
}

/**
 * Returns an HSL color string for an agent avatar.
 * Fixed saturation 65%, lightness 60%.
 */
export function agentColor(agentId: string): string {
  return `hsl(${agentHue(agentId)}, 65%, 60%)`;
}
