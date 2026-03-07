import "./AppShell.css";
import { TopBar } from "./TopBar";
import { HistoryPane } from "./HistoryPane";
import { ChatPane } from "./ChatPane";
import { IntelligencePane } from "./IntelligencePane";
import { BottomControls } from "./BottomControls";

export function AppShell() {
  return (
    <div className="app-shell" data-testid="app-shell">
      <TopBar />
      <section className="app-shell__main" data-testid="main-content">
        <HistoryPane />
        <ChatPane />
        <IntelligencePane />
      </section>
      <BottomControls />
    </div>
  );
}
