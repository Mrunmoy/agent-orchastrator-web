import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the app shell layout", () => {
    render(<App />);
    expect(screen.getByTestId("app-shell")).toBeInTheDocument();
  });

  it("renders all four layout zones", () => {
    render(<App />);
    expect(screen.getByTestId("top-bar")).toBeInTheDocument();
    expect(screen.getByTestId("history-pane")).toBeInTheDocument();
    expect(screen.getByTestId("chat-pane")).toBeInTheDocument();
    expect(screen.getByTestId("intelligence-pane")).toBeInTheDocument();
    expect(screen.getByTestId("bottom-controls")).toBeInTheDocument();
  });
});
