import React from "react";
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { AgreementBar } from "./AgreementBar";
import type { AgentPosition } from "./types";

const positions: AgentPosition[] = [
  {
    agent_id: "a1",
    agent_name: "Alice",
    position: "strong_agree",
    summary: "Fully on board",
  },
  {
    agent_id: "a2",
    agent_name: "Bob",
    position: "agree",
    summary: "Mostly agrees",
  },
  {
    agent_id: "a3",
    agent_name: "Carol",
    position: "disagree",
    summary: "Has concerns",
  },
  {
    agent_id: "a4",
    agent_name: "Dave",
    position: "strong_agree",
    summary: "Very supportive",
  },
];

describe("AgreementBar", () => {
  it("renders the agreement bar container", () => {
    render(<AgreementBar positions={positions} />);
    expect(screen.getByTestId("agreement-bar")).toBeInTheDocument();
  });

  it("renders segments for each agreement level present", () => {
    render(<AgreementBar positions={positions} />);
    const bar = screen.getByTestId("agreement-bar");

    const strongAgree = bar.querySelector(".segment-strong_agree");
    const agree = bar.querySelector(".segment-agree");
    const disagree = bar.querySelector(".segment-disagree");

    expect(strongAgree).toBeInTheDocument();
    expect(agree).toBeInTheDocument();
    expect(disagree).toBeInTheDocument();

    // neutral and strong_disagree should not be present
    expect(bar.querySelector(".segment-neutral")).not.toBeInTheDocument();
    expect(
      bar.querySelector(".segment-strong_disagree")
    ).not.toBeInTheDocument();
  });

  it("shows agent count in each segment", () => {
    render(<AgreementBar positions={positions} />);
    // strong_agree has 2 agents (Alice, Dave)
    expect(screen.getByText("2")).toBeInTheDocument();
    // agree and disagree each have 1
    const ones = screen.getAllByText("1");
    expect(ones.length).toBe(2);
  });

  it("shows agent names in title attribute for hover", () => {
    render(<AgreementBar positions={positions} />);
    const bar = screen.getByTestId("agreement-bar");

    const strongAgree = bar.querySelector(".segment-strong_agree");
    expect(strongAgree?.getAttribute("title")).toContain("Alice");
    expect(strongAgree?.getAttribute("title")).toContain("Dave");
  });

  it("renders nothing when positions is empty", () => {
    render(<AgreementBar positions={[]} />);
    const bar = screen.getByTestId("agreement-bar");
    // No segments should be rendered
    expect(bar.children.length).toBe(0);
  });
});
