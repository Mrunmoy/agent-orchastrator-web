import { FormEvent, useMemo, useState } from "react";
import "./TopBar.css";

const WORKING_DIR_KEY = "ao_working_dir";
const WORKING_DIR_HISTORY_KEY = "ao_working_dir_history";
const DEFAULT_WORKING_DIR = "/home/user/workspace";

function readStorage(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}

function writeStorage(key: string, value: string): void {
  try {
    window.localStorage.setItem(key, value);
  } catch {
    // Ignore storage failures in restricted environments.
  }
}

type TopBarProps = {
  runStatus?: string;
  gateStatus?: string;
  onRunNewBatch?: () => void;
  onStopRun?: () => void;
};

export function TopBar({
  runStatus = "Idle",
  gateStatus = "Open",
  onRunNewBatch,
  onStopRun,
}: TopBarProps) {
  const initialWorkingDir = readStorage(WORKING_DIR_KEY) ?? DEFAULT_WORKING_DIR;
  const initialHistory = useMemo(() => {
    const raw = readStorage(WORKING_DIR_HISTORY_KEY);
    if (!raw) {
      return [initialWorkingDir];
    }
    try {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        return parsed.filter((entry): entry is string => typeof entry === "string");
      }
      return [initialWorkingDir];
    } catch {
      return [initialWorkingDir];
    }
  }, [initialWorkingDir]);

  const [workingDir, setWorkingDir] = useState(initialWorkingDir);
  const [history, setHistory] = useState<string[]>(initialHistory);

  const saveWorkingDir = () => {
    const trimmed = workingDir.trim();
    if (!trimmed) return;
    writeStorage(WORKING_DIR_KEY, trimmed);
    const nextHistory = [trimmed, ...history.filter((entry) => entry !== trimmed)].slice(0, 10);
    setHistory(nextHistory);
    writeStorage(WORKING_DIR_HISTORY_KEY, JSON.stringify(nextHistory));
    setWorkingDir(trimmed);
  };

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    saveWorkingDir();
  };

  return (
    <header className="top-bar" data-testid="top-bar">
      <div className="top-bar__title">
        Agent Orchestrator Lab
        <span className="chip">Phase: TDD Planning</span>
        <span className="chip">Gate: {gateStatus}</span>
      </div>
      <form className="top-bar__field" onSubmit={onSubmit}>
        <label htmlFor="working-dir">Working Directory</label>
        <div className="top-bar__working-dir-row">
          <input
            id="working-dir"
            list="working-dir-history"
            value={workingDir}
            onChange={(event) => setWorkingDir(event.target.value)}
            placeholder="/path/to/project"
          />
          <button className="btn btn--secondary" type="submit">
            Save
          </button>
          <datalist id="working-dir-history">
            {history.map((entry) => (
              <option key={entry} value={entry} />
            ))}
          </datalist>
        </div>
      </form>
      <div className="top-bar__status" data-testid="run-status">
        {runStatus}
      </div>
      <button className="btn btn--primary" onClick={onRunNewBatch}>
        Run New Batch (20)
      </button>
      <button className="btn btn--danger" onClick={onStopRun}>
        Stop Current Run
      </button>
    </header>
  );
}
