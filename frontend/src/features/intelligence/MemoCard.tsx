import React from "react";
import type { NeutralMemo } from "./types";
import "./MemoCard.css";

interface MemoCardProps {
  memo: NeutralMemo | null;
}

export const MemoCard: React.FC<MemoCardProps> = ({ memo }) => {
  if (!memo) {
    return (
      <div className="memo-card memo-empty" data-testid="memo-empty">
        No memo available
      </div>
    );
  }

  return (
    <div className="memo-card" data-testid="memo-card">
      <h3 className="memo-card-heading">Neutral Memo</h3>
      <p className="memo-card-summary">{memo.summary}</p>
      <h4 className="memo-card-subheading">Key Points</h4>
      <ul className="memo-card-points">
        {memo.key_points.map((point, idx) => (
          <li key={idx}>{point}</li>
        ))}
      </ul>
      <h4 className="memo-card-subheading">Recommendation</h4>
      <p className="memo-card-recommendation">{memo.recommendation}</p>
      <span className="memo-card-timestamp">{memo.generated_at}</span>
    </div>
  );
};
