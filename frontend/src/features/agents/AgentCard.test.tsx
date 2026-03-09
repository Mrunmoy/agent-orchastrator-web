import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { AgentCard } from "./AgentCard";
import type { AgentData } from "./types";

const mockAgent: AgentData = {
  id: "agent-1",
  display_name: "Claude Worker",
  provider: "claude",
  model: "opus-4",
  role: "worker",
  status: "idle",
  sort_order: 0,
};

describe("AgentCard", () => {
  it("shows display_name", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    expect(screen.getByText("Claude Worker")).toBeInTheDocument();
  });

  it("shows provider badge with correct class", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const badge = screen.getByText("claude");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("provider-claude");
  });

  it("shows model name", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    expect(screen.getByText("opus-4")).toBeInTheDocument();
  });

  it("shows role badge", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    expect(screen.getByText("worker")).toBeInTheDocument();
  });

  it("shows status indicator with correct class", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const status = screen.getByTestId("status-indicator");
    expect(status.className).toContain("status-dot-idle");
  });

  it("edit button calls onEdit with agent id", () => {
    const onEdit = vi.fn();
    render(<AgentCard agent={mockAgent} onEdit={onEdit} />);
    fireEvent.click(screen.getByRole("button", { name: /edit/i }));
    expect(onEdit).toHaveBeenCalledWith("agent-1");
  });

  it("renders order badge showing sort_order + 1 when no turn_order", () => {
    render(<AgentCard agent={{ ...mockAgent, sort_order: 0 }} onEdit={() => {}} />);
    expect(screen.getByTestId("order-badge")).toHaveTextContent("1");
  });

  it("renders order badge with correct position for sort_order 2 when no turn_order", () => {
    render(<AgentCard agent={{ ...mockAgent, sort_order: 2 }} onEdit={() => {}} />);
    expect(screen.getByTestId("order-badge")).toHaveTextContent("3");
  });

  it("renders order badge showing turn_order directly when present", () => {
    render(<AgentCard agent={{ ...mockAgent, sort_order: 0, turn_order: 3 }} onEdit={() => {}} />);
    expect(screen.getByTestId("order-badge")).toHaveTextContent("3");
  });

  // --- New tests for redesigned card ---

  it("renders avatar with first letter of display name", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const avatar = screen.getByTestId("agent-avatar");
    expect(avatar).toHaveTextContent("C");
  });

  it("applies provider-specific color class to avatar", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const avatar = screen.getByTestId("agent-avatar");
    expect(avatar.className).toContain("provider-avatar-claude");
    expect(avatar.style.backgroundColor).toBe("rgb(97, 31, 105)");
  });

  it("applies codex provider color to avatar", () => {
    const codexAgent: AgentData = { ...mockAgent, provider: "codex" };
    render(<AgentCard agent={codexAgent} onEdit={() => {}} />);
    const avatar = screen.getByTestId("agent-avatar");
    expect(avatar.className).toContain("provider-avatar-codex");
    expect(avatar.style.backgroundColor).toBe("rgb(43, 172, 118)");
  });

  it("applies ollama provider color to avatar", () => {
    const ollamaAgent: AgentData = { ...mockAgent, provider: "ollama" };
    render(<AgentCard agent={ollamaAgent} onEdit={() => {}} />);
    const avatar = screen.getByTestId("agent-avatar");
    expect(avatar.className).toContain("provider-avatar-ollama");
    expect(avatar.style.backgroundColor).toBe("rgb(18, 100, 163)");
  });

  it("applies gemini provider color to avatar", () => {
    const geminiAgent: AgentData = { ...mockAgent, provider: "gemini" };
    render(<AgentCard agent={geminiAgent} onEdit={() => {}} />);
    const avatar = screen.getByTestId("agent-avatar");
    expect(avatar.className).toContain("provider-avatar-gemini");
    expect(avatar.style.backgroundColor).toBe("rgb(236, 178, 46)");
  });

  it("shows status indicator dot with idle class", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const dot = screen.getByTestId("status-indicator");
    expect(dot.className).toContain("agent-card-status-dot");
    expect(dot.className).toContain("status-dot-idle");
  });

  it("shows status indicator dot with running class", () => {
    const runningAgent: AgentData = { ...mockAgent, status: "running" };
    render(<AgentCard agent={runningAgent} onEdit={() => {}} />);
    const dot = screen.getByTestId("status-indicator");
    expect(dot.className).toContain("status-dot-running");
  });

  it("shows status indicator dot with offline class", () => {
    const offlineAgent: AgentData = { ...mockAgent, status: "offline" };
    render(<AgentCard agent={offlineAgent} onEdit={() => {}} />);
    const dot = screen.getByTestId("status-indicator");
    expect(dot.className).toContain("status-dot-offline");
  });

  it("shows status indicator dot with blocked class", () => {
    const blockedAgent: AgentData = { ...mockAgent, status: "blocked" };
    render(<AgentCard agent={blockedAgent} onEdit={() => {}} />);
    const dot = screen.getByTestId("status-indicator");
    expect(dot.className).toContain("status-dot-blocked");
  });

  it("displays personality tag when personality_key is set", () => {
    const agentWithPersonality: AgentData = {
      ...mockAgent,
      personality_key: "devil_advocate",
    };
    render(<AgentCard agent={agentWithPersonality} onEdit={() => {}} />);
    const tag = screen.getByTestId("personality-tag");
    expect(tag).toHaveTextContent("Devil Advocate");
  });

  it("does not display personality tag when personality_key is not set", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    expect(screen.queryByTestId("personality-tag")).not.toBeInTheDocument();
  });

  it("shows model name in dedicated element", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const model = screen.getByTestId("agent-model");
    expect(model).toHaveTextContent("opus-4");
  });

  it("shows role badge", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const badge = screen.getByTestId("role-badge");
    expect(badge).toHaveTextContent("worker");
  });

  it("shows coordinator role badge", () => {
    const coordAgent: AgentData = { ...mockAgent, role: "coordinator" };
    render(<AgentCard agent={coordAgent} onEdit={() => {}} />);
    const badge = screen.getByTestId("role-badge");
    expect(badge).toHaveTextContent("coordinator");
  });

  it("has data-testid with agent id", () => {
    render(<AgentCard agent={mockAgent} onEdit={() => {}} />);
    const card = screen.getByTestId("agent-card");
    expect(card.getAttribute("data-agent-testid")).toBe("agent-card-agent-1");
  });
});
