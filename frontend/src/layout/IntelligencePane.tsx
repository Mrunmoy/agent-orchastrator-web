import "./IntelligencePane.css";

type IntelligencePaneProps = {
  agreementSummary?: string;
  conflictSummary?: string;
  memoSummary?: string;
};

export function IntelligencePane({
  agreementSummary = "No agreements recorded yet.",
  conflictSummary = "No conflicts recorded yet.",
  memoSummary = "No memo available.",
}: IntelligencePaneProps) {
  return (
    <aside className="panel intel-pane" data-testid="intelligence-pane">
      <h3>Batch Intelligence</h3>
      <div className="intel-pane__scroll">
        <div className="intel-card intel-card--ok" data-testid="agreement-section">
          <h4>Agreement Map</h4>
          <p className="intel-card__empty">{agreementSummary}</p>
        </div>
        <div className="intel-card intel-card--warn" data-testid="conflict-section">
          <h4>Conflict Map</h4>
          <p className="intel-card__empty">{conflictSummary}</p>
        </div>
        <div className="intel-card intel-card--memo" data-testid="memo-section">
          <h4>Neutral Memo</h4>
          <p className="intel-card__empty">{memoSummary}</p>
        </div>
      </div>
    </aside>
  );
}
