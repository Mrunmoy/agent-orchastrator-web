import "./IntelligencePane.css";

export function IntelligencePane() {
  return (
    <aside className="panel intel-pane" data-testid="intelligence-pane">
      <h3>Batch Intelligence</h3>
      <div className="intel-pane__scroll">
        <div className="intel-card intel-card--ok" data-testid="agreement-section">
          <h4>Agreement Map</h4>
          <p className="intel-card__empty">No agreements recorded yet.</p>
        </div>
        <div className="intel-card intel-card--warn" data-testid="conflict-section">
          <h4>Conflict Map</h4>
          <p className="intel-card__empty">No conflicts recorded yet.</p>
        </div>
        <div className="intel-card intel-card--memo" data-testid="memo-section">
          <h4>Neutral Memo</h4>
          <p className="intel-card__empty">No memo available.</p>
        </div>
      </div>
    </aside>
  );
}
