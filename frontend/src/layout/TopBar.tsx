import "./TopBar.css";

export function TopBar() {
  return (
    <header className="top-bar" data-testid="top-bar">
      <div className="top-bar__title">
        Agent Orchestrator Lab
        <span className="chip">Phase: TDD Planning</span>
        <span className="chip">Gate: Open</span>
      </div>
      <div className="top-bar__field">
        <label htmlFor="working-dir">Working Directory</label>
        <select id="working-dir">
          <option>/home/user/workspace</option>
        </select>
      </div>
      <div className="top-bar__status" data-testid="run-status">
        Idle
      </div>
      <button className="btn btn--primary">Run New Batch (20)</button>
      <button className="btn btn--danger">Stop Current Run</button>
    </header>
  );
}
