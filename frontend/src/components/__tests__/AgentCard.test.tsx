import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AgentCard } from "../AgentCard";

const baseAgent = {
  id: "a1",
  display_name: "Alpha Agent",
  provider: "claude",
  model: "claude-opus-4-5",
  role: "worker",
  status: "idle",
};

describe("AgentCard", () => {
  it("renders agent display name", () => {
    render(<AgentCard agent={baseAgent} />);
    expect(screen.getByText("Alpha Agent")).toBeInTheDocument();
  });

  it("renders agent status", () => {
    render(<AgentCard agent={baseAgent} />);
    expect(screen.getByText("idle")).toBeInTheDocument();
  });

  it("renders model badge", () => {
    render(<AgentCard agent={baseAgent} />);
    expect(screen.getByText("claude-opus-4-5")).toBeInTheDocument();
  });

  it("renders role badge", () => {
    render(<AgentCard agent={baseAgent} />);
    expect(screen.getByText("worker")).toBeInTheDocument();
  });

  it("renders provider badge", () => {
    render(<AgentCard agent={baseAgent} />);
    expect(screen.getByText("claude")).toBeInTheDocument();
  });

  it("renders avatar fallback with initials", () => {
    render(<AgentCard agent={baseAgent} />);
    expect(screen.getByText("AL")).toBeInTheDocument();
  });

  it("renders personality key when present", () => {
    render(<AgentCard agent={{ ...baseAgent, personality_key: "Tech Lead" }} />);
    expect(screen.getByText("Tech Lead")).toBeInTheDocument();
  });

  it("does not render personality when absent", () => {
    render(<AgentCard agent={baseAgent} />);
    expect(screen.queryByText("Tech Lead")).not.toBeInTheDocument();
  });

  it("renders coordinator role", () => {
    render(<AgentCard agent={{ ...baseAgent, role: "coordinator" }} />);
    expect(screen.getByText("coordinator")).toBeInTheDocument();
  });

  it("renders different providers", () => {
    render(<AgentCard agent={{ ...baseAgent, provider: "codex" }} />);
    expect(screen.getByText("codex")).toBeInTheDocument();
  });

  it("renders running status", () => {
    render(<AgentCard agent={{ ...baseAgent, status: "running" }} />);
    expect(screen.getByText("running")).toBeInTheDocument();
  });

  it("renders offline status", () => {
    render(<AgentCard agent={{ ...baseAgent, status: "offline" }} />);
    expect(screen.getByText("offline")).toBeInTheDocument();
  });
});
