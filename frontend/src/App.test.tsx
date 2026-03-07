import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import App from "./App";

describe("App", () => {
  it("renders the app shell heading", () => {
    render(<App />);
    expect(screen.getByRole("heading", { name: /agent orchestrator/i })).toBeInTheDocument();
  });

  it("renders the root layout element", () => {
    const { container } = render(<App />);
    expect(container.querySelector("[data-testid='app-shell']")).toBeInTheDocument();
  });
});
