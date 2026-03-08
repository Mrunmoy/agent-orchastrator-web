export type TaskStatus =
  | "todo"
  | "design"
  | "tdd"
  | "implementing"
  | "testing"
  | "pr_raised"
  | "in_review"
  | "fixing_comments"
  | "merging"
  | "done";

export interface KanbanTask {
  id: string;
  title: string;
  status: TaskStatus;
  assignee?: string;
  priority?: "low" | "medium" | "high" | "critical";
}

export interface KanbanColumn {
  status: TaskStatus;
  label: string;
}

export const KANBAN_COLUMNS: KanbanColumn[] = [
  { status: "todo", label: "Todo" },
  { status: "design", label: "Design" },
  { status: "tdd", label: "TDD" },
  { status: "implementing", label: "Implementing" },
  { status: "testing", label: "Testing" },
  { status: "pr_raised", label: "PR Raised" },
  { status: "in_review", label: "In Review" },
  { status: "fixing_comments", label: "Fixing Comments" },
  { status: "merging", label: "Merging" },
  { status: "done", label: "Done" },
];
