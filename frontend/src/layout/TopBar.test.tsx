import { fireEvent, render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { TopBar } from "./TopBar";

describe("TopBar", () => {
  it("renders the top bar container", () => {
    render(<TopBar />);
    expect(screen.getByTestId("top-bar")).toBeInTheDocument();
  });

  it("displays the app title", () => {
    render(<TopBar />);
    expect(screen.getByText("Agent Orchestrator Lab")).toBeInTheDocument();
  });

  it("renders the working directory input", () => {
    render(<TopBar />);
    expect(screen.getByLabelText("Working Directory")).toBeInTheDocument();
  });

  it("allows editing and saving the working directory", () => {
    render(<TopBar />);
    const input = screen.getByLabelText("Working Directory");
    fireEvent.change(input, { target: { value: "/tmp/my-project" } });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    expect(window.localStorage.getItem("ao_working_dir")).toBe("/tmp/my-project");
  });

  it("renders a status indicator", () => {
    render(<TopBar />);
    expect(screen.getByTestId("run-status")).toBeInTheDocument();
  });

  it("renders run batch button", () => {
    render(<TopBar />);
    expect(screen.getByRole("button", { name: /run.*batch/i })).toBeInTheDocument();
  });

  it("renders stop button", () => {
    render(<TopBar />);
    expect(screen.getByRole("button", { name: /stop/i })).toBeInTheDocument();
  });
});
