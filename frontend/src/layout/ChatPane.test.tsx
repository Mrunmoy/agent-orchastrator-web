import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { ChatPane } from "./ChatPane";

describe("ChatPane", () => {
  it("renders the chat pane container", () => {
    render(<ChatPane />);
    expect(screen.getByTestId("chat-pane")).toBeInTheDocument();
  });

  it("displays the Group Debate heading", () => {
    render(<ChatPane />);
    expect(screen.getByText("Group Debate")).toBeInTheDocument();
  });

  it("renders the ChatTimeline area", () => {
    render(<ChatPane />);
    expect(screen.getByTestId("chat-timeline")).toBeInTheDocument();
  });

  it("renders the composer area", () => {
    render(<ChatPane />);
    expect(screen.getByTestId("composer")).toBeInTheDocument();
  });

  it("renders a send button in the composer", () => {
    render(<ChatPane />);
    expect(screen.getByRole("button", { name: /send/i })).toBeInTheDocument();
  });
});
