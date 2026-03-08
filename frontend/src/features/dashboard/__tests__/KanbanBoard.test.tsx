import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { KanbanBoard } from "../KanbanBoard";
import type { KanbanTask } from "../types";
import { KANBAN_COLUMNS } from "../types";

const SAMPLE_TASKS: KanbanTask[] = [
  { id: "UI-001", title: "Build top bar", status: "done", assignee: "claude" },
  {
    id: "UI-002",
    title: "History pane",
    status: "implementing",
    assignee: "codex",
  },
  { id: "UI-003", title: "Chat pane", status: "tdd" },
  { id: "UI-004", title: "Intelligence pane", status: "todo" },
  { id: "UI-005", title: "Bottom controls", status: "design" },
  {
    id: "UI-006",
    title: "PR workflow",
    status: "pr_raised",
    assignee: "claude",
  },
  { id: "UI-007", title: "Code review", status: "in_review" },
  { id: "UI-008", title: "Fix lint", status: "fixing_comments" },
  { id: "UI-009", title: "Deploy pipeline", status: "merging" },
  { id: "UI-010", title: "E2E tests", status: "testing" },
];

describe("KanbanBoard", () => {
  // TT-307-01: Renders all 10 status columns with correct headers
  it("renders all 10 status columns with correct headers", () => {
    render(<KanbanBoard tasks={[]} />);

    for (const col of KANBAN_COLUMNS) {
      expect(
        screen.getByTestId(`kanban-column-${col.status}`),
      ).toBeInTheDocument();
      expect(screen.getByText(col.label)).toBeInTheDocument();
    }

    const columns = screen.getAllByTestId(/^kanban-column-/);
    expect(columns).toHaveLength(10);
  });

  // TT-307-02: Shows task count in each column header
  it("shows task count in each column header", () => {
    render(<KanbanBoard tasks={SAMPLE_TASKS} />);

    // Each sample task is in a different column, so each count should be 1
    for (const col of KANBAN_COLUMNS) {
      const countEl = screen.getByTestId(`kanban-count-${col.status}`);
      expect(countEl).toHaveTextContent("1");
    }
  });

  it("shows zero count for empty columns", () => {
    render(<KanbanBoard tasks={[]} />);

    for (const col of KANBAN_COLUMNS) {
      const countEl = screen.getByTestId(`kanban-count-${col.status}`);
      expect(countEl).toHaveTextContent("0");
    }
  });

  // TT-307-03: Empty columns have dimmed styling
  it("empty columns have dimmed styling", () => {
    const tasks: KanbanTask[] = [
      { id: "T-1", title: "A task", status: "todo" },
    ];
    render(<KanbanBoard tasks={tasks} />);

    // The "todo" column should NOT be dimmed
    const todoCol = screen.getByTestId("kanban-column-todo");
    expect(todoCol).not.toHaveClass("kanban-column--empty");

    // All other columns should be dimmed
    const emptyStatuses = KANBAN_COLUMNS.filter((c) => c.status !== "todo");
    for (const col of emptyStatuses) {
      const colEl = screen.getByTestId(`kanban-column-${col.status}`);
      expect(colEl).toHaveClass("kanban-column--empty");
    }
  });

  // TT-307-04: Tasks render in the correct column based on status
  it("tasks render in the correct column based on status", () => {
    render(<KanbanBoard tasks={SAMPLE_TASKS} />);

    // Verify each task card exists
    for (const task of SAMPLE_TASKS) {
      expect(screen.getByTestId(`kanban-card-${task.id}`)).toBeInTheDocument();
      expect(screen.getByText(task.title)).toBeInTheDocument();
    }

    // Verify tasks are inside the correct column
    const todoCol = screen.getByTestId("kanban-column-todo");
    expect(todoCol).toContainElement(
      screen.getByTestId("kanban-card-UI-004"),
    );

    const implCol = screen.getByTestId("kanban-column-implementing");
    expect(implCol).toContainElement(
      screen.getByTestId("kanban-card-UI-002"),
    );

    const doneCol = screen.getByTestId("kanban-column-done");
    expect(doneCol).toContainElement(
      screen.getByTestId("kanban-card-UI-001"),
    );
  });

  it("displays task ID and assignee in card meta", () => {
    render(<KanbanBoard tasks={SAMPLE_TASKS} />);

    // Check a task with assignee
    const card = screen.getByTestId("kanban-card-UI-001");
    expect(card).toHaveTextContent("UI-001");
    expect(card).toHaveTextContent("claude");

    // Check a task without assignee
    const card3 = screen.getByTestId("kanban-card-UI-003");
    expect(card3).toHaveTextContent("UI-003");
  });
});
