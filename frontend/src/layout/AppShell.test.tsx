import { fireEvent, render, screen, within } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AppShell } from "./AppShell";

describe("AppShell", () => {
  it("renders the root layout container", () => {
    render(<AppShell />);
    expect(screen.getByTestId("app-shell")).toBeInTheDocument();
  });

  it("renders the top bar region", () => {
    render(<AppShell />);
    expect(screen.getByTestId("top-bar")).toBeInTheDocument();
  });

  it("renders the history pane (left)", () => {
    render(<AppShell />);
    expect(screen.getByTestId("history-pane")).toBeInTheDocument();
  });

  it("renders the chat pane (center)", () => {
    render(<AppShell />);
    expect(screen.getByTestId("chat-pane")).toBeInTheDocument();
  });

  it("renders the intelligence pane (right)", () => {
    render(<AppShell />);
    expect(screen.getByTestId("intelligence-pane")).toBeInTheDocument();
  });

  it("renders the bottom controls", () => {
    render(<AppShell />);
    expect(screen.getByTestId("bottom-controls")).toBeInTheDocument();
  });

  it("applies grid layout class on the root container", () => {
    render(<AppShell />);
    const shell = screen.getByTestId("app-shell");
    expect(shell.className).toContain("app-shell");
  });

  it("applies grid layout class for the main content area", () => {
    render(<AppShell />);
    const main = screen.getByTestId("main-content");
    expect(main.className).toContain("app-shell__main");
  });

  it("creates a new conversation when New is clicked", () => {
    render(<AppShell />);
    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
    const list = screen.getByTestId("conversation-list");
    expect(within(list).getByText("Conversation 1")).toBeInTheDocument();
  });

  it("sends a message to the active conversation", () => {
    render(<AppShell />);
    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
    fireEvent.change(screen.getByPlaceholderText("Type a message..."), {
      target: { value: "hello agents" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send to group/i }));
    expect(screen.getByText("hello agents")).toBeInTheDocument();
  });

  it("clear all removes conversations", () => {
    render(<AppShell />);
    fireEvent.click(screen.getByRole("button", { name: /\+ new/i }));
    fireEvent.click(screen.getByRole("button", { name: /clear all/i }));
    expect(screen.getByText("No conversations yet")).toBeInTheDocument();
  });
});
