import "./BottomControls.css";

export function BottomControls() {
  return (
    <section className="bottom-controls" data-testid="bottom-controls">
      <div className="bottom-controls__field">
        <label htmlFor="steering-note">Steering Note</label>
        <textarea id="steering-note" rows={2} />
      </div>
      <div className="bottom-controls__field">
        <label htmlFor="preference-note">Preference Note</label>
        <textarea id="preference-note" rows={2} />
      </div>
      <button className="btn btn--ok">Continue Batch (20) With Notes</button>
      <button className="btn btn--subtle">Mark Gate Ready For My Review</button>
    </section>
  );
}
