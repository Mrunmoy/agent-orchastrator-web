import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { BottomControls } from "./BottomControls";

describe("BottomControls", () => {
  it("renders the bottom controls container", () => {
    render(<BottomControls />);
    expect(screen.getByTestId("bottom-controls")).toBeInTheDocument();
  });

  it("renders the steering note textarea", () => {
    render(<BottomControls />);
    expect(screen.getByLabelText("Steering Note")).toBeInTheDocument();
  });

  it("renders the preference note textarea", () => {
    render(<BottomControls />);
    expect(screen.getByLabelText("Preference Note")).toBeInTheDocument();
  });

  it("renders the continue batch button", () => {
    render(<BottomControls />);
    expect(screen.getByRole("button", { name: /continue.*batch/i })).toBeInTheDocument();
  });

  it("renders the gate review button", () => {
    render(<BottomControls />);
    expect(screen.getByRole("button", { name: /gate.*review/i })).toBeInTheDocument();
  });
});
