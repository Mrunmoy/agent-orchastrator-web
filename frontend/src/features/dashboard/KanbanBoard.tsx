import "./KanbanBoard.css";
import { KANBAN_COLUMNS, type KanbanTask } from "./types";

type KanbanBoardProps = {
  tasks: KanbanTask[];
};

export function KanbanBoard({ tasks }: KanbanBoardProps) {
  const tasksByStatus = new Map<string, KanbanTask[]>();
  for (const col of KANBAN_COLUMNS) {
    tasksByStatus.set(col.status, []);
  }
  for (const task of tasks) {
    const list = tasksByStatus.get(task.status);
    if (list) {
      list.push(task);
    }
  }

  return (
    <div className="kanban-board" data-testid="kanban-board">
      {KANBAN_COLUMNS.map((col) => {
        const columnTasks = tasksByStatus.get(col.status) ?? [];
        const isEmpty = columnTasks.length === 0;

        return (
          <div
            key={col.status}
            className={`kanban-column kanban-column--${col.status}${isEmpty ? " kanban-column--empty" : ""}`}
            data-testid={`kanban-column-${col.status}`}
          >
            <div className="kanban-column__header">
              <span className="kanban-column__title">{col.label}</span>
              <span className="kanban-column__count" data-testid={`kanban-count-${col.status}`}>
                {columnTasks.length}
              </span>
            </div>
            <div className="kanban-column__body">
              {columnTasks.map((task) => (
                <div key={task.id} className="kanban-card" data-testid={`kanban-card-${task.id}`}>
                  <div className="kanban-card__title">{task.title}</div>
                  <div className="kanban-card__meta">
                    <span className="kanban-card__id">{task.id}</span>
                    {task.assignee && (
                      <span className="kanban-card__assignee">{task.assignee}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}
