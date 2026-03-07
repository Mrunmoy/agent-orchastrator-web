import React from "react";
import type { IntelligenceData } from "./types";
import { AgreementBar } from "./AgreementBar";
import { MemoCard } from "./MemoCard";
import "./IntelligencePane.css";

interface IntelligencePaneProps {
  data: IntelligenceData | null;
}

export const IntelligencePane: React.FC<IntelligencePaneProps> = ({ data }) => {
  if (!data) {
    return (
      <div
        className="intelligence-pane intelligence-empty"
        data-testid="intelligence-empty"
      >
        No intelligence data
      </div>
    );
  }

  return (
    <div className="intelligence-pane" data-testid="intelligence-pane">
      <h2 className="intelligence-pane-title">Intelligence</h2>
      <section className="intelligence-section">
        <h3 className="intelligence-section-title">Agreement</h3>
        <AgreementBar positions={data.positions} />
      </section>
      <section className="intelligence-section">
        <MemoCard memo={data.memo} />
      </section>
    </div>
  );
};
