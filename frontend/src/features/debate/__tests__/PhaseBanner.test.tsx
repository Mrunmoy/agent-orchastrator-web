import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { PhaseBanner } from "../PhaseBanner";

describe("PhaseBanner — T-304", () => {
  // TT-304-01: Renders phase name and round counter
  describe("TT-304-01: phase name and round counter", () => {
    it("renders the phase name", () => {
      render(
        <PhaseBanner phase="Design Debate" round={5} totalRounds={20} />,
      );
      expect(screen.getByTestId("phase-name")).toHaveTextContent(
        "Design Debate",
      );
    });

    it("renders the round counter with correct format", () => {
      render(
        <PhaseBanner phase="Design Debate" round={5} totalRounds={20} />,
      );
      expect(screen.getByTestId("round-counter")).toHaveTextContent(
        "Round 5/20",
      );
    });

    it("renders inside a sticky banner element", () => {
      render(
        <PhaseBanner phase="TDD Planning" round={1} totalRounds={10} />,
      );
      expect(screen.getByTestId("phase-banner")).toBeInTheDocument();
    });
  });

  // TT-304-02: Shows speaking indicator with agent name when agent is generating
  describe("TT-304-02: speaking indicator visible", () => {
    it("shows speaking indicator with agent name", () => {
      render(
        <PhaseBanner
          phase="Design Debate"
          round={3}
          totalRounds={20}
          speakingAgent="Claude"
        />,
      );
      const indicator = screen.getByTestId("speaking-indicator");
      expect(indicator).toBeInTheDocument();
      expect(indicator).toHaveTextContent("Claude");
    });

    it("renders animated dots inside speaking indicator", () => {
      render(
        <PhaseBanner
          phase="Implementation"
          round={7}
          totalRounds={20}
          speakingAgent="Codex"
        />,
      );
      const indicator = screen.getByTestId("speaking-indicator");
      const dots = indicator.querySelectorAll(".phase-banner__speaking-dot");
      expect(dots).toHaveLength(3);
    });
  });

  // TT-304-03: Hides speaking indicator when no agent is speaking
  describe("TT-304-03: speaking indicator hidden", () => {
    it("does not render speaking indicator when speakingAgent is null", () => {
      render(
        <PhaseBanner
          phase="Design Debate"
          round={1}
          totalRounds={20}
          speakingAgent={null}
        />,
      );
      expect(
        screen.queryByTestId("speaking-indicator"),
      ).not.toBeInTheDocument();
    });

    it("does not render speaking indicator when speakingAgent is omitted", () => {
      render(
        <PhaseBanner phase="Design Debate" round={1} totalRounds={20} />,
      );
      expect(
        screen.queryByTestId("speaking-indicator"),
      ).not.toBeInTheDocument();
    });
  });
});
