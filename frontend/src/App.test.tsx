import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the agent workspace heading", () => {
    render(<App />);
    expect(screen.getByText("Agent Workspace")).toBeInTheDocument();
  });

  it("renders the sidebar with conversations section", () => {
    render(<App />);
    expect(screen.getByText("Conversations")).toBeInTheDocument();
  });

  it("renders the direct messages section", () => {
    render(<App />);
    expect(screen.getByText("Direct Messages")).toBeInTheDocument();
  });
});
