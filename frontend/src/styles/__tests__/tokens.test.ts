import { describe, it, expect, beforeAll } from "vitest";
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const tokensCssPath = resolve(__dirname, "..", "tokens.css");

let cssText: string;

describe("Design Tokens", () => {
  beforeAll(() => {
    cssText = readFileSync(tokensCssPath, "utf-8");
  });

  it("tokens.css is importable without errors", async () => {
    // Verify the dynamic import doesn't throw
    await import("../tokens.css");
  });

  it("defines core OKLch color custom properties on :root", () => {
    const colorProps = [
      "--color-primary",
      "--color-accent",
      "--color-warning",
      "--color-error",
      "--color-info",
      "--color-success",
    ];

    for (const prop of colorProps) {
      expect(cssText).toContain(prop);
    }
  });

  it("defines surface and sidebar colors", () => {
    const expectedProps = ["--color-bg", "--color-surface", "--color-sidebar-bg", "--color-brand"];

    for (const prop of expectedProps) {
      expect(cssText).toContain(prop);
    }
  });

  it("defines spacing scale from --space-1 through --space-8", () => {
    for (let i = 1; i <= 8; i++) {
      expect(cssText).toContain(`--space-${i}`);
    }
  });

  it("defines radius scale", () => {
    const radiusProps = ["--radius-sm", "--radius-md", "--radius-lg", "--radius-xl"];
    for (const prop of radiusProps) {
      expect(cssText).toContain(prop);
    }
  });

  it("defines shadow scale", () => {
    const shadowProps = ["--shadow-sm", "--shadow-md", "--shadow-lg"];
    for (const prop of shadowProps) {
      expect(cssText).toContain(prop);
    }
  });

  it("defines font family tokens including Space Grotesk and JetBrains Mono", () => {
    expect(cssText).toContain("--font-heading");
    expect(cssText).toContain("--font-body");
    expect(cssText).toContain("--font-mono");
    expect(cssText).toContain("Space Grotesk");
    expect(cssText).toContain("JetBrains Mono");
  });

  it("defines font size scale from --text-xs through --text-2xl", () => {
    const sizes = ["--text-xs", "--text-sm", "--text-base", "--text-lg", "--text-xl", "--text-2xl"];
    for (const prop of sizes) {
      expect(cssText).toContain(prop);
    }
  });

  it("defines transition tokens", () => {
    expect(cssText).toContain("--transition-fast");
    expect(cssText).toContain("--transition-normal");
  });
});
