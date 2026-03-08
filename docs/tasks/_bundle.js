window.__TASK_DATA__ = {
  "api-tasks": [
    {
      "id": "T-201",
      "title": "Conversation detail and update endpoints",
      "description": "Implement GET /api/conversations/{id} returning full conversation details (phase, gate_status, agent count, task count) and PATCH /api/conversations/{id} for updating title, project_path, and other metadata fields. The GET endpoint joins conversation_agent and task tables to include counts. PATCH validates that the conversation exists and is not soft-deleted. Acceptance criteria: GET returns enriched conversation object with agent_count and task_count; PATCH updates only provided fields; both use standard envelope.",
      "design_refs": [
        "DES-01",
        "DES-02"
      ],
      "requirements": [
        "BE-R071",
        "BE-R060"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/conversations.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/"
        ]
      },
      "complexity": "S",
      "parallel_group": "api-conversations",
      "tests": [
        {
          "id": "TT-201-01",
          "description": "GET /api/conversations/{id} returns full details with agent_count and task_count",
          "type": "integration",
          "file": "backend/tests/test_api_conversations.py"
        },
        {
          "id": "TT-201-02",
          "description": "GET /api/conversations/{id} returns 404 for non-existent or soft-deleted conversation",
          "type": "integration",
          "file": "backend/tests/test_api_conversations.py"
        },
        {
          "id": "TT-201-03",
          "description": "PATCH /api/conversations/{id} updates title and project_path, returns updated object",
          "type": "integration",
          "file": "backend/tests/test_api_conversations.py"
        },
        {
          "id": "TT-201-04",
          "description": "PATCH /api/conversations/{id} ignores null fields and returns 404 for missing conversation",
          "type": "integration",
          "file": "backend/tests/test_api_conversations.py"
        }
      ]
    },
    {
      "id": "T-202",
      "title": "Message CRUD endpoints",
      "description": "Implement POST /api/conversations/{id}/messages to send a customer message (with optional target_agent_id for directed messages) and GET /api/conversations/{id}/messages for paginated message retrieval with ?after=event_id cursor and ?limit=N. POST creates a message_event row with source_type='customer', event_type='chat_message', and a generated UUID event_id. GET returns events ordered by auto-increment id. Acceptance criteria: POST persists message and returns it; GET supports cursor-based pagination; directed messages include target_agent_id in metadata_json.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R090",
        "BE-R030",
        "BE-R031",
        "BE-R032",
        "BE-R060"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/messages.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "M",
      "parallel_group": "api-messages",
      "tests": [
        {
          "id": "TT-202-01",
          "description": "POST /api/conversations/{id}/messages creates a customer message event and returns it",
          "type": "integration",
          "file": "backend/tests/test_api_messages.py"
        },
        {
          "id": "TT-202-02",
          "description": "POST with target_agent_id stores directed message metadata",
          "type": "integration",
          "file": "backend/tests/test_api_messages.py"
        },
        {
          "id": "TT-202-03",
          "description": "GET /api/conversations/{id}/messages returns paginated results with ?after cursor",
          "type": "integration",
          "file": "backend/tests/test_api_messages.py"
        },
        {
          "id": "TT-202-04",
          "description": "GET /api/conversations/{id}/messages returns 404 for non-existent conversation",
          "type": "integration",
          "file": "backend/tests/test_api_messages.py"
        }
      ]
    },
    {
      "id": "T-203",
      "title": "Event filtering endpoint",
      "description": "Implement GET /api/conversations/{id}/events returning all events for a conversation filterable by ?event_type= query parameter. Supports multiple event types via comma-separated values. Returns events from the message_event SQLite table (not just JSONL), ordered by id ascending. Acceptance criteria: filtering by single and multiple event_types works; unfiltered returns all events; returns 404 for missing conversation.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R091",
        "BE-R031",
        "BE-R060"
      ],
      "dependencies": [
        "T-101",
        "T-202"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/messages.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "S",
      "parallel_group": "api-messages",
      "tests": [
        {
          "id": "TT-203-01",
          "description": "GET /api/conversations/{id}/events returns all events unfiltered",
          "type": "integration",
          "file": "backend/tests/test_api_messages.py"
        },
        {
          "id": "TT-203-02",
          "description": "GET with ?event_type=chat_message filters correctly",
          "type": "integration",
          "file": "backend/tests/test_api_messages.py"
        },
        {
          "id": "TT-203-03",
          "description": "GET with multiple event_type values (comma-separated) returns matching events",
          "type": "integration",
          "file": "backend/tests/test_api_messages.py"
        }
      ]
    },
    {
      "id": "T-204",
      "title": "Task CRUD endpoints",
      "description": "Implement GET /api/conversations/{id}/tasks to list tasks for a conversation, POST /api/conversations/{id}/tasks to create a task, and PATCH /api/tasks/{task_id} to update task status, owner, result, and evidence. POST accepts title, spec_json, priority, depends_on_json, and optional owner_agent_id. PATCH validates status transitions per BE-R021 (todo -> design -> tdd -> implementing -> testing -> pr_raised -> in_review -> fixing_comments -> merging -> done, plus blocked from any state). Acceptance criteria: CRUD works end-to-end; invalid status transitions return 400; dependency JSON is stored and returned correctly.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R100",
        "BE-R020",
        "BE-R021",
        "BE-R022",
        "BE-R060"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/tasks.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "L",
      "parallel_group": "api-tasks",
      "tests": [
        {
          "id": "TT-204-01",
          "description": "POST /api/conversations/{id}/tasks creates a task with spec_json and returns it",
          "type": "integration",
          "file": "backend/tests/test_api_tasks.py"
        },
        {
          "id": "TT-204-02",
          "description": "GET /api/conversations/{id}/tasks lists all tasks ordered by priority",
          "type": "integration",
          "file": "backend/tests/test_api_tasks.py"
        },
        {
          "id": "TT-204-03",
          "description": "PATCH /api/tasks/{id} updates status through valid transitions",
          "type": "integration",
          "file": "backend/tests/test_api_tasks.py"
        },
        {
          "id": "TT-204-04",
          "description": "PATCH /api/tasks/{id} rejects invalid status transitions with 400",
          "type": "integration",
          "file": "backend/tests/test_api_tasks.py"
        }
      ]
    },
    {
      "id": "T-205",
      "title": "Task dependency validation",
      "description": "Add dependency enforcement to task status transitions. When PATCH /api/tasks/{task_id} attempts to transition a task to 'implementing', verify that all task IDs listed in depends_on_json have status 'done'. If any dependency is not done, return 409 Conflict with a list of blocking dependency IDs. Acceptance criteria: transition to implementing blocked when deps not done; transition allowed when all deps are done; tasks with empty depends_on_json can transition freely.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R022",
        "BE-R150"
      ],
      "dependencies": [
        "T-204"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/tasks.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "M",
      "parallel_group": "api-tasks",
      "tests": [
        {
          "id": "TT-205-01",
          "description": "Task with unmet dependencies cannot transition to implementing, returns 409",
          "type": "integration",
          "file": "backend/tests/test_api_tasks.py"
        },
        {
          "id": "TT-205-02",
          "description": "Task with all dependencies done can transition to implementing",
          "type": "integration",
          "file": "backend/tests/test_api_tasks.py"
        },
        {
          "id": "TT-205-03",
          "description": "Task with empty depends_on_json transitions freely",
          "type": "unit",
          "file": "backend/tests/test_api_tasks.py"
        }
      ]
    },
    {
      "id": "T-206",
      "title": "Phase and gate endpoints",
      "description": "Implement GET /api/conversations/{id}/phase returning current phase and gate_status, and POST /api/conversations/{id}/gate to advance the gate. Gate advancement follows the phase sequence: design_debate -> task_planning -> execution -> review -> merge -> done. POST /gate accepts action ('approve' or 'reject'). On approve: gate_status -> 'approved', then phase advances to next phase and gate_status resets to 'open'. On reject: gate_status -> 'rejected', phase stays. Acceptance criteria: phase sequence is enforced; approve advances phase; reject keeps phase; already-done conversation returns 409.",
      "design_refs": [
        "DES-01",
        "DES-02"
      ],
      "requirements": [
        "BE-R001",
        "BE-R060"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/phases.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "M",
      "parallel_group": "api-conversations",
      "tests": [
        {
          "id": "TT-206-01",
          "description": "GET /api/conversations/{id}/phase returns current phase and gate_status",
          "type": "integration",
          "file": "backend/tests/test_api_phases.py"
        },
        {
          "id": "TT-206-02",
          "description": "POST /gate with approve advances phase to next in sequence",
          "type": "integration",
          "file": "backend/tests/test_api_phases.py"
        },
        {
          "id": "TT-206-03",
          "description": "POST /gate with reject sets gate_status to rejected, phase unchanged",
          "type": "integration",
          "file": "backend/tests/test_api_phases.py"
        },
        {
          "id": "TT-206-04",
          "description": "POST /gate on a done conversation returns 409",
          "type": "integration",
          "file": "backend/tests/test_api_phases.py"
        }
      ]
    },
    {
      "id": "T-207",
      "title": "Merge queue endpoints",
      "description": "Implement merge queue CRUD: GET /api/conversations/{id}/merge-queue lists queued items ordered by position, POST /api/conversations/{id}/merge-queue enqueues a task (sets position to max+1, status='queued'), PATCH /api/merge-queue/{item_id} updates status (queued -> rebasing -> testing -> merging -> merged | failed | blocked), and DELETE /api/merge-queue/{item_id} removes an item and recompacts positions. POST requires task_id, pr_number, pr_url, pr_branch, author_agent_id, and optional reviewer_agent_id. Acceptance criteria: FIFO ordering maintained; only one item can be 'merging' at a time; position recompaction on delete.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R060"
      ],
      "dependencies": [
        "T-101",
        "T-204"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/merge_queue.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "L",
      "parallel_group": "api-tasks",
      "tests": [
        {
          "id": "TT-207-01",
          "description": "POST /merge-queue enqueues item at next position with status queued",
          "type": "integration",
          "file": "backend/tests/test_api_merge_queue.py"
        },
        {
          "id": "TT-207-02",
          "description": "GET /merge-queue returns items ordered by position",
          "type": "integration",
          "file": "backend/tests/test_api_merge_queue.py"
        },
        {
          "id": "TT-207-03",
          "description": "PATCH /merge-queue/{id} rejects merging when another item is already merging",
          "type": "integration",
          "file": "backend/tests/test_api_merge_queue.py"
        },
        {
          "id": "TT-207-04",
          "description": "DELETE /merge-queue/{id} removes item and recompacts positions",
          "type": "integration",
          "file": "backend/tests/test_api_merge_queue.py"
        }
      ]
    },
    {
      "id": "T-208",
      "title": "SSE conversation stream endpoint",
      "description": "Implement GET /api/conversations/{id}/stream as a Server-Sent Events endpoint using FastAPI StreamingResponse. The endpoint streams new message_events for a conversation in real-time. Uses an async generator that polls for new events by auto-increment id (last seen id tracked per connection). SSE envelope format: 'id: {event_id}\\nevent: {event_type}\\ndata: {json_payload}\\n\\n'. Supports Last-Event-ID header for reconnection \u2014 replays missed events from the store. Sends heartbeat comments every 15 seconds to keep connection alive. Acceptance criteria: SSE stream delivers new events; reconnection via Last-Event-ID replays missed events; heartbeat keeps connection open.",
      "design_refs": [
        "DES-01"
      ],
      "requirements": [
        "BE-R120",
        "BE-R122",
        "BE-R060"
      ],
      "dependencies": [
        "T-101",
        "T-202"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/streams.py",
          "backend/src/agent_orchestrator/api/sse.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/"
        ]
      },
      "complexity": "L",
      "parallel_group": "api-streaming",
      "tests": [
        {
          "id": "TT-208-01",
          "description": "SSE stream delivers events in correct SSE envelope format",
          "type": "integration",
          "file": "backend/tests/test_api_streams.py"
        },
        {
          "id": "TT-208-02",
          "description": "Last-Event-ID header causes replay of missed events",
          "type": "integration",
          "file": "backend/tests/test_api_streams.py"
        },
        {
          "id": "TT-208-03",
          "description": "Heartbeat comments are sent to keep connection alive",
          "type": "integration",
          "file": "backend/tests/test_api_streams.py"
        },
        {
          "id": "TT-208-04",
          "description": "Stream returns 404 for non-existent conversation",
          "type": "integration",
          "file": "backend/tests/test_api_streams.py"
        }
      ]
    },
    {
      "id": "T-209",
      "title": "SSE agent activity stream endpoint",
      "description": "Implement GET /api/agents/{id}/activity as a Server-Sent Events endpoint for per-agent activity. Streams agent-specific events: thinking output, tool calls, file reads/writes, shell commands, and their results. Uses the same SSE envelope format as T-208. Events are sourced from message_event rows where source_id matches the agent_id and event_type is in the activity category. Supports Last-Event-ID for reconnection. Acceptance criteria: stream delivers only events for the specified agent; activity event types are correctly filtered; reconnection works.",
      "design_refs": [
        "DES-01"
      ],
      "requirements": [
        "BE-R121",
        "BE-R122",
        "BE-R060"
      ],
      "dependencies": [
        "T-208"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/streams.py",
          "backend/src/agent_orchestrator/api/sse.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/"
        ]
      },
      "complexity": "M",
      "parallel_group": "api-streaming",
      "tests": [
        {
          "id": "TT-209-01",
          "description": "Agent activity stream delivers only events for the specified agent",
          "type": "integration",
          "file": "backend/tests/test_api_streams.py"
        },
        {
          "id": "TT-209-02",
          "description": "Activity stream filters to activity-related event types",
          "type": "integration",
          "file": "backend/tests/test_api_streams.py"
        },
        {
          "id": "TT-209-03",
          "description": "Agent activity stream supports Last-Event-ID reconnection",
          "type": "integration",
          "file": "backend/tests/test_api_streams.py"
        }
      ]
    },
    {
      "id": "T-210",
      "title": "SSE infrastructure: event bus and broadcaster",
      "description": "Implement an in-process event bus (asyncio-based) that routes new events to SSE stream subscribers. Components: EventBus class with publish(event) and subscribe(filter) -> AsyncIterator methods. When a message_event is inserted (via POST message, steer, or orchestration), the bus publishes the event. SSE stream endpoints subscribe with filters (conversation_id, agent_id). This replaces the polling approach in T-208/T-209 with push-based delivery. Acceptance criteria: events published to bus are received by all matching subscribers; unsubscribe on disconnect cleans up; bus handles multiple concurrent subscribers.",
      "design_refs": [
        "DES-01"
      ],
      "requirements": [
        "BE-R120",
        "BE-R121"
      ],
      "dependencies": [
        "T-208"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/event_bus.py",
          "backend/src/agent_orchestrator/api/sse.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/"
        ]
      },
      "complexity": "L",
      "parallel_group": "api-streaming",
      "tests": [
        {
          "id": "TT-210-01",
          "description": "EventBus delivers published events to all matching subscribers",
          "type": "unit",
          "file": "backend/tests/test_event_bus.py"
        },
        {
          "id": "TT-210-02",
          "description": "Subscriber with conversation_id filter only receives events for that conversation",
          "type": "unit",
          "file": "backend/tests/test_event_bus.py"
        },
        {
          "id": "TT-210-03",
          "description": "Disconnected subscriber is cleaned up and does not block bus",
          "type": "unit",
          "file": "backend/tests/test_event_bus.py"
        },
        {
          "id": "TT-210-04",
          "description": "Multiple concurrent subscribers receive events independently",
          "type": "unit",
          "file": "backend/tests/test_event_bus.py"
        }
      ]
    },
    {
      "id": "T-211",
      "title": "API error handling middleware",
      "description": "Implement a FastAPI exception handler middleware that catches all unhandled exceptions and returns the standard error envelope ({ok: false, error: message}) with appropriate HTTP status codes. Handle: ValidationError -> 400, HTTPException -> its status code, NotFoundError (custom) -> 404, ConflictError (custom) -> 409, generic Exception -> 500 with sanitized message. Define custom exception classes (NotFoundError, ConflictError, ValidationError) in a new exceptions module. Register the handler in create_app(). Acceptance criteria: all error responses use the envelope format; validation errors include field-level details; 500 errors do not leak stack traces.",
      "design_refs": [
        "DES-01"
      ],
      "requirements": [
        "BE-R150",
        "BE-R060"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/exceptions.py",
          "backend/src/agent_orchestrator/api/middleware.py",
          "backend/src/agent_orchestrator/api/__init__.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/"
        ]
      },
      "complexity": "M",
      "parallel_group": "api-conversations",
      "tests": [
        {
          "id": "TT-211-01",
          "description": "Unhandled exceptions return 500 with envelope format and no stack trace",
          "type": "integration",
          "file": "backend/tests/test_api_middleware.py"
        },
        {
          "id": "TT-211-02",
          "description": "Pydantic ValidationError returns 400 with field-level error details",
          "type": "integration",
          "file": "backend/tests/test_api_middleware.py"
        },
        {
          "id": "TT-211-03",
          "description": "Custom NotFoundError returns 404 with envelope",
          "type": "integration",
          "file": "backend/tests/test_api_middleware.py"
        },
        {
          "id": "TT-211-04",
          "description": "Custom ConflictError returns 409 with envelope",
          "type": "integration",
          "file": "backend/tests/test_api_middleware.py"
        }
      ]
    },
    {
      "id": "T-212",
      "title": "Agent status tracking endpoints",
      "description": "Implement GET /api/agents/{id}/status returning current agent status (idle, running, blocked, offline) and PATCH /api/agents/{id}/status for updating status with validated transitions. Status transitions: idle -> running (task assigned), running -> idle (turn complete), running -> blocked (waiting), blocked -> idle (unblocked), any -> offline (process died). Status changes emit a system event (event_type='agent_status_change') to the conversation's message_event table. Acceptance criteria: GET returns current status; PATCH validates transitions; status change creates system event.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R131",
        "BE-R010",
        "BE-R060"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/agents.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "M",
      "parallel_group": "api-agents",
      "tests": [
        {
          "id": "TT-212-01",
          "description": "GET /api/agents/{id}/status returns current status",
          "type": "integration",
          "file": "backend/tests/test_api_agents.py"
        },
        {
          "id": "TT-212-02",
          "description": "PATCH /api/agents/{id}/status accepts valid transition idle -> running",
          "type": "integration",
          "file": "backend/tests/test_api_agents.py"
        },
        {
          "id": "TT-212-03",
          "description": "PATCH /api/agents/{id}/status rejects invalid transition idle -> blocked",
          "type": "integration",
          "file": "backend/tests/test_api_agents.py"
        },
        {
          "id": "TT-212-04",
          "description": "Status change emits agent_status_change system event",
          "type": "integration",
          "file": "backend/tests/test_api_agents.py"
        }
      ]
    },
    {
      "id": "T-213",
      "title": "Agent-to-conversation assignment endpoint",
      "description": "Implement POST /api/conversations/{id}/agents to add an existing agent to a conversation. Accepts agent_id and optional permission_profile and is_merge_coordinator fields. Auto-assigns turn_order as max(existing) + 1. Enforces UNIQUE(conversation_id, agent_id) constraint \u2014 returns 409 if agent already in conversation. Validates both conversation and agent exist. Acceptance criteria: agent is linked to conversation with correct turn_order; duplicate assignment returns 409; is_merge_coordinator flag is stored.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R011",
        "BE-R012",
        "BE-R013",
        "BE-R060"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/conversation_agents.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "S",
      "parallel_group": "api-agents",
      "tests": [
        {
          "id": "TT-213-01",
          "description": "POST /api/conversations/{id}/agents links agent with auto-assigned turn_order",
          "type": "integration",
          "file": "backend/tests/test_api_conversation_agents.py"
        },
        {
          "id": "TT-213-02",
          "description": "Duplicate agent assignment returns 409 Conflict",
          "type": "integration",
          "file": "backend/tests/test_api_conversation_agents.py"
        },
        {
          "id": "TT-213-03",
          "description": "is_merge_coordinator flag is stored and returned correctly",
          "type": "integration",
          "file": "backend/tests/test_api_conversation_agents.py"
        }
      ]
    },
    {
      "id": "T-214",
      "title": "Agent process failure event surfacing",
      "description": "Implement error event creation for agent process failures. Add a utility function create_agent_failure_event(conversation_id, agent_id, error_type, message) that inserts a message_event with event_type='system_notice', source_type='system', and metadata containing the error details (error_type: 'crash'|'timeout'|'rate_limit', agent_id, traceback summary). Integrate this with the adapter layer's error handling. Acceptance criteria: agent failures create system_notice events; events appear in conversation timeline; metadata includes error classification.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R151",
        "BE-R030",
        "BE-R031"
      ],
      "dependencies": [
        "T-101",
        "T-202"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/messages.py",
          "backend/src/agent_orchestrator/orchestrator/error_events.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/",
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "api-agents",
      "tests": [
        {
          "id": "TT-214-01",
          "description": "create_agent_failure_event inserts system_notice event with correct metadata",
          "type": "unit",
          "file": "backend/tests/test_error_events.py"
        },
        {
          "id": "TT-214-02",
          "description": "Crash error event includes agent_id and error classification in metadata",
          "type": "unit",
          "file": "backend/tests/test_error_events.py"
        },
        {
          "id": "TT-214-03",
          "description": "Failure events appear in GET /api/conversations/{id}/messages timeline",
          "type": "integration",
          "file": "backend/tests/test_error_events.py"
        }
      ]
    },
    {
      "id": "T-215",
      "title": "Register new route modules in FastAPI app",
      "description": "Update the FastAPI application factory (create_app in api/__init__.py) to include all new routers created in T-202 through T-210: messages, tasks, phases, merge_queue, and streams. Add the router imports and include_router calls with the /api prefix. Verify all endpoints are accessible and do not conflict with existing routes. Acceptance criteria: all new endpoints are reachable; no route conflicts; OpenAPI schema includes all endpoints.",
      "design_refs": [
        "DES-01"
      ],
      "requirements": [
        "BE-R061"
      ],
      "dependencies": [
        "T-202",
        "T-204",
        "T-206",
        "T-207",
        "T-208"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/__init__.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/"
        ]
      },
      "complexity": "S",
      "parallel_group": "api-conversations",
      "tests": [
        {
          "id": "TT-215-01",
          "description": "All new route modules are included in the FastAPI app",
          "type": "integration",
          "file": "backend/tests/test_api_app.py"
        },
        {
          "id": "TT-215-02",
          "description": "OpenAPI schema includes all new endpoints under /api prefix",
          "type": "integration",
          "file": "backend/tests/test_api_app.py"
        },
        {
          "id": "TT-215-03",
          "description": "No route path conflicts between existing and new routers",
          "type": "integration",
          "file": "backend/tests/test_api_app.py"
        }
      ]
    }
  ],
  "foundation-tasks": [
    {
      "id": "T-101",
      "title": "Database schema migration v4: merge_queue table",
      "description": "Add the merge_queue table (DES-02) to schema.sql and create migration v4 in db.py. The table tracks serialized merge queue entries with fields: id, conversation_id, task_id, pr_number, pr_url, pr_branch, author_agent_id, reviewer_agent_id, position, status, queued_at, merged_at, created_at. Add appropriate indexes. Acceptance criteria: (1) schema.sql includes merge_queue with all columns and FK constraints, (2) migration v4 in _MIGRATIONS creates the table idempotently, (3) _SCHEMA_VERSION bumped to 4, (4) existing databases migrate cleanly.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "MG-R060",
        "MG-R061",
        "BE-R051"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/schema.sql",
          "backend/src/agent_orchestrator/storage/db.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/"
        ]
      },
      "complexity": "S",
      "parallel_group": "foundation-schema",
      "tests": [
        {
          "id": "TT-101-01",
          "description": "Test that initialize() on a fresh DB creates the merge_queue table with all expected columns",
          "type": "unit",
          "file": "backend/tests/test_schema_merge_queue.py"
        },
        {
          "id": "TT-101-02",
          "description": "Test that migration from v3 to v4 adds merge_queue without data loss in existing tables",
          "type": "integration",
          "file": "backend/tests/test_schema_merge_queue.py"
        },
        {
          "id": "TT-101-03",
          "description": "Test that merge_queue FK constraints enforce valid conversation_id, task_id, and author_agent_id references",
          "type": "unit",
          "file": "backend/tests/test_schema_merge_queue.py"
        }
      ]
    },
    {
      "id": "T-102",
      "title": "Database schema: add missing FK constraints and indexes",
      "description": "Harden existing schema.sql by adding FK constraints on task.conversation_id -> conversation(id), task.owner_agent_id -> agent(id), artifact.conversation_id -> conversation(id), message_event.conversation_id -> conversation(id), message_event.source_id -> agent(id). Add migration v5 to apply these on existing databases (requires table recreation for SQLite FK additions). Also add index on message_event(event_id) for SSE Last-Event-ID lookups. Acceptance criteria: (1) all FK constraints enforced, (2) migration is idempotent, (3) indexes exist for FK columns.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R001",
        "BE-R020",
        "BE-R030",
        "BE-R040",
        "BE-R051"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/schema.sql",
          "backend/src/agent_orchestrator/storage/db.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-schema",
      "tests": [
        {
          "id": "TT-102-01",
          "description": "Test that inserting a task with invalid conversation_id raises IntegrityError",
          "type": "unit",
          "file": "backend/tests/test_schema_fk.py"
        },
        {
          "id": "TT-102-02",
          "description": "Test that inserting an artifact with invalid conversation_id raises IntegrityError",
          "type": "unit",
          "file": "backend/tests/test_schema_fk.py"
        },
        {
          "id": "TT-102-03",
          "description": "Test that inserting a message_event with invalid conversation_id raises IntegrityError",
          "type": "unit",
          "file": "backend/tests/test_schema_fk.py"
        },
        {
          "id": "TT-102-04",
          "description": "Test that migration from v4 to v5 preserves existing data while adding constraints",
          "type": "integration",
          "file": "backend/tests/test_schema_fk.py"
        }
      ]
    },
    {
      "id": "T-103",
      "title": "Storage abstraction layer: repository interfaces",
      "description": "Create abstract repository interfaces (ABCs) for each entity: ConversationRepository, AgentRepository, TaskRepository, MessageEventRepository, ArtifactRepository, MergeQueueRepository. Define method signatures for CRUD operations (create, get_by_id, list, update, delete). Place in backend/src/agent_orchestrator/storage/repositories/__init__.py with individual files per entity. This decouples route handlers from raw SQL and enables future backend swaps. Acceptance criteria: (1) all ABCs defined with type-hinted signatures, (2) methods match the data model entities from DES-02, (3) no concrete implementation yet (separate tasks).",
      "design_refs": [
        "DES-01",
        "DES-02"
      ],
      "requirements": [
        "BE-R001",
        "BE-R010",
        "BE-R020",
        "BE-R030",
        "BE-R040",
        "BE-R050"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/__init__.py",
          "backend/src/agent_orchestrator/storage/repositories/base.py",
          "backend/src/agent_orchestrator/storage/repositories/conversation.py",
          "backend/src/agent_orchestrator/storage/repositories/agent.py",
          "backend/src/agent_orchestrator/storage/repositories/task.py",
          "backend/src/agent_orchestrator/storage/repositories/message_event.py",
          "backend/src/agent_orchestrator/storage/repositories/artifact.py",
          "backend/src/agent_orchestrator/storage/repositories/merge_queue.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-schema",
      "tests": [
        {
          "id": "TT-103-01",
          "description": "Test that all repository ABCs cannot be instantiated directly (abstract methods enforced)",
          "type": "unit",
          "file": "backend/tests/test_repository_interfaces.py"
        },
        {
          "id": "TT-103-02",
          "description": "Test that all repository ABCs define the required CRUD method signatures with correct type hints",
          "type": "unit",
          "file": "backend/tests/test_repository_interfaces.py"
        },
        {
          "id": "TT-103-03",
          "description": "Test that a minimal concrete subclass can be created by implementing all abstract methods",
          "type": "unit",
          "file": "backend/tests/test_repository_interfaces.py"
        }
      ]
    },
    {
      "id": "T-104",
      "title": "Conversation CRUD repository (SQLite implementation)",
      "description": "Implement SQLiteConversationRepository that fulfills the ConversationRepository ABC. Methods: create(title, project_path) -> Conversation, get_by_id(id) -> Conversation|None, list_active() -> list[Conversation] (excludes soft-deleted), update(id, fields) -> Conversation, soft_delete(id), clear_all(), select(id) (deactivate all others, activate target). Must use the Conversation dataclass from orchestrator/models.py. Refactor existing conversations.py route handlers to use this repository instead of inline SQL. Acceptance criteria: (1) all methods implemented with proper transactions, (2) soft-delete filters in list, (3) select atomically deactivates others, (4) routes use repository.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R001",
        "BE-R002",
        "BE-R003",
        "BE-R050"
      ],
      "dependencies": [
        "T-103"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/sqlite_conversation.py",
          "backend/src/agent_orchestrator/api/routes/conversations.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/",
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-crud",
      "tests": [
        {
          "id": "TT-104-01",
          "description": "Test create conversation returns a Conversation with generated UUID, correct defaults for phase/gate_status/active",
          "type": "unit",
          "file": "backend/tests/test_conversation_repo.py"
        },
        {
          "id": "TT-104-02",
          "description": "Test soft_delete sets deleted_at and list_active excludes the deleted conversation",
          "type": "unit",
          "file": "backend/tests/test_conversation_repo.py"
        },
        {
          "id": "TT-104-03",
          "description": "Test select atomically deactivates all others and activates the target conversation",
          "type": "unit",
          "file": "backend/tests/test_conversation_repo.py"
        },
        {
          "id": "TT-104-04",
          "description": "Test clear_all soft-deletes all conversations and returns the count",
          "type": "unit",
          "file": "backend/tests/test_conversation_repo.py"
        }
      ]
    },
    {
      "id": "T-105",
      "title": "Agent CRUD repository (SQLite implementation)",
      "description": "Implement SQLiteAgentRepository fulfilling the AgentRepository ABC. Methods: create(display_name, provider, model, role, personality_key?) -> Agent, get_by_id(id) -> Agent|None, list_all() -> list[Agent] (ordered by sort_order, display_name), update(id, fields) -> Agent, delete(id) (hard delete, cascade remove from conversation_agent), update_sort_order(id, order). Validate provider against Provider enum and role against AgentRole enum. Refactor agents.py route handlers to use this repository. Acceptance criteria: (1) all CRUD methods implemented, (2) provider/role validation, (3) cascade delete removes conversation_agent rows, (4) routes use repository.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R010",
        "BE-R050"
      ],
      "dependencies": [
        "T-103"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/sqlite_agent.py",
          "backend/src/agent_orchestrator/api/routes/agents.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/",
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-crud",
      "tests": [
        {
          "id": "TT-105-01",
          "description": "Test create agent with valid provider/role returns Agent with generated UUID and idle status",
          "type": "unit",
          "file": "backend/tests/test_agent_repo.py"
        },
        {
          "id": "TT-105-02",
          "description": "Test create agent with invalid provider raises ValueError",
          "type": "unit",
          "file": "backend/tests/test_agent_repo.py"
        },
        {
          "id": "TT-105-03",
          "description": "Test delete agent cascades to remove conversation_agent join rows",
          "type": "integration",
          "file": "backend/tests/test_agent_repo.py"
        },
        {
          "id": "TT-105-04",
          "description": "Test list_all returns agents ordered by sort_order ascending, then display_name",
          "type": "unit",
          "file": "backend/tests/test_agent_repo.py"
        }
      ]
    },
    {
      "id": "T-106",
      "title": "Conversation-Agent join repository (SQLite implementation)",
      "description": "Implement SQLiteConversationAgentRepository for managing the conversation_agent join table. Methods: add_agent_to_conversation(conversation_id, agent_id, permission_profile?) -> ConversationAgent (auto-assigns turn_order as max+1), remove_agent(conversation_id, agent_id), list_agents(conversation_id) -> list with turn_order, reorder(conversation_id, agent_ids: list[str]), set_merge_coordinator(conversation_id, agent_id). Enforce UNIQUE(conversation_id, agent_id). Refactor conversation_agents.py route handlers. Acceptance criteria: (1) turn_order auto-increment works, (2) reorder updates all turn_orders atomically, (3) merge coordinator flag is exclusive per conversation.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R011",
        "BE-R012",
        "BE-R013"
      ],
      "dependencies": [
        "T-103",
        "T-104",
        "T-105"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/sqlite_conversation_agent.py",
          "backend/src/agent_orchestrator/api/routes/conversation_agents.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/",
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-crud",
      "tests": [
        {
          "id": "TT-106-01",
          "description": "Test add_agent auto-assigns turn_order as max(existing)+1, starting from 1",
          "type": "unit",
          "file": "backend/tests/test_conversation_agent_repo.py"
        },
        {
          "id": "TT-106-02",
          "description": "Test adding same agent to same conversation twice raises IntegrityError (UNIQUE constraint)",
          "type": "unit",
          "file": "backend/tests/test_conversation_agent_repo.py"
        },
        {
          "id": "TT-106-03",
          "description": "Test reorder updates turn_order for all agents atomically in the specified order",
          "type": "unit",
          "file": "backend/tests/test_conversation_agent_repo.py"
        },
        {
          "id": "TT-106-04",
          "description": "Test set_merge_coordinator clears existing coordinator and sets the new one",
          "type": "unit",
          "file": "backend/tests/test_conversation_agent_repo.py"
        }
      ]
    },
    {
      "id": "T-107",
      "title": "Task CRUD repository (SQLite implementation)",
      "description": "Implement SQLiteTaskRepository fulfilling the TaskRepository ABC. Methods: create(conversation_id, title, spec_json, priority?, depends_on?) -> Task, get_by_id(id) -> Task|None, list_by_conversation(conversation_id, status_filter?) -> list[Task], update_status(id, status) with validation against TaskStatus enum and dependency checks, assign_owner(id, agent_id), update_result(id, result_summary, evidence_json). Task status transitions: validate that implementing cannot be entered unless all depends_on tasks are done. Acceptance criteria: (1) all CRUD methods implemented, (2) dependency check blocks invalid status transitions, (3) status values match BE-R021 enum.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R020",
        "BE-R021",
        "BE-R022",
        "BE-R050"
      ],
      "dependencies": [
        "T-103"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/sqlite_task.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/"
        ]
      },
      "complexity": "L",
      "parallel_group": "foundation-crud",
      "tests": [
        {
          "id": "TT-107-01",
          "description": "Test create task returns Task with default status 'todo' and correct conversation_id",
          "type": "unit",
          "file": "backend/tests/test_task_repo.py"
        },
        {
          "id": "TT-107-02",
          "description": "Test update_status to 'implementing' is blocked when dependency tasks are not 'done'",
          "type": "unit",
          "file": "backend/tests/test_task_repo.py"
        },
        {
          "id": "TT-107-03",
          "description": "Test update_status to 'implementing' succeeds when all dependency tasks are 'done'",
          "type": "unit",
          "file": "backend/tests/test_task_repo.py"
        },
        {
          "id": "TT-107-04",
          "description": "Test list_by_conversation with status_filter returns only matching tasks",
          "type": "unit",
          "file": "backend/tests/test_task_repo.py"
        }
      ]
    },
    {
      "id": "T-108",
      "title": "MessageEvent CRUD repository (SQLite implementation)",
      "description": "Implement SQLiteMessageEventRepository fulfilling the MessageEventRepository ABC. Methods: append(conversation_id, source_type, source_id, text, event_type, metadata_json?) -> MessageEvent (generates UUID event_id), get_by_event_id(event_id) -> MessageEvent|None, list_by_conversation(conversation_id, after_id?, limit?) -> list[MessageEvent] for pagination, list_by_type(conversation_id, event_type) -> list[MessageEvent]. Events are append-only: no update or delete methods. Validate event_type against BE-R031 taxonomy. Acceptance criteria: (1) all methods implemented, (2) append generates UUID event_id, (3) pagination via after_id works correctly, (4) no update/delete methods exist.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R030",
        "BE-R031",
        "BE-R032",
        "BE-R050"
      ],
      "dependencies": [
        "T-103"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/sqlite_message_event.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-crud",
      "tests": [
        {
          "id": "TT-108-01",
          "description": "Test append creates a message_event with unique UUID event_id and auto-increment id",
          "type": "unit",
          "file": "backend/tests/test_message_event_repo.py"
        },
        {
          "id": "TT-108-02",
          "description": "Test list_by_conversation with after_id returns only events after the specified cursor",
          "type": "unit",
          "file": "backend/tests/test_message_event_repo.py"
        },
        {
          "id": "TT-108-03",
          "description": "Test list_by_type filters events to only the specified event_type",
          "type": "unit",
          "file": "backend/tests/test_message_event_repo.py"
        },
        {
          "id": "TT-108-04",
          "description": "Test that repository exposes no update or delete methods (append-only enforcement)",
          "type": "unit",
          "file": "backend/tests/test_message_event_repo.py"
        }
      ]
    },
    {
      "id": "T-109",
      "title": "Artifact CRUD repository (SQLite implementation)",
      "description": "Implement SQLiteArtifactRepository fulfilling the ArtifactRepository ABC. Methods: create(conversation_id, type, payload_json, batch_id?) -> Artifact, get_by_id(id) -> Artifact|None, list_by_conversation(conversation_id, type_filter?) -> list[Artifact] ordered by created_at DESC, get_latest(conversation_id) -> Artifact|None. Validate type against ArtifactType enum (design_doc, task_plan, summary, checkpoint, agreement_map, etc.). Acceptance criteria: (1) all methods implemented, (2) type validation, (3) get_latest returns most recent artifact for a conversation.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R040",
        "BE-R050"
      ],
      "dependencies": [
        "T-103"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/sqlite_artifact.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/"
        ]
      },
      "complexity": "S",
      "parallel_group": "foundation-crud",
      "tests": [
        {
          "id": "TT-109-01",
          "description": "Test create artifact returns Artifact with generated UUID and correct type",
          "type": "unit",
          "file": "backend/tests/test_artifact_repo.py"
        },
        {
          "id": "TT-109-02",
          "description": "Test list_by_conversation with type_filter returns only matching artifact types",
          "type": "unit",
          "file": "backend/tests/test_artifact_repo.py"
        },
        {
          "id": "TT-109-03",
          "description": "Test get_latest returns the most recently created artifact for a conversation",
          "type": "unit",
          "file": "backend/tests/test_artifact_repo.py"
        }
      ]
    },
    {
      "id": "T-110",
      "title": "MergeQueue CRUD repository (SQLite implementation)",
      "description": "Implement SQLiteMergeQueueRepository fulfilling the MergeQueueRepository ABC. Methods: enqueue(conversation_id, task_id, author_agent_id, pr_number?, pr_url?, pr_branch?) -> MergeQueueEntry (auto-assigns position as max+1), get_by_id(id) -> entry|None, list_by_conversation(conversation_id) -> list ordered by position, update_status(id, status), assign_reviewer(id, reviewer_agent_id), reorder(conversation_id, entry_ids), get_current_merging(conversation_id) -> entry|None. Enforce: only one entry can have status='merging' at a time per conversation. Acceptance criteria: (1) all methods implemented, (2) position auto-increment, (3) merging exclusivity enforced.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "MG-R060",
        "MG-R061",
        "BE-R050"
      ],
      "dependencies": [
        "T-101",
        "T-103"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/repositories/sqlite_merge_queue.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/repositories/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-crud",
      "tests": [
        {
          "id": "TT-110-01",
          "description": "Test enqueue auto-assigns position as max(existing)+1 for the conversation",
          "type": "unit",
          "file": "backend/tests/test_merge_queue_repo.py"
        },
        {
          "id": "TT-110-02",
          "description": "Test update_status to 'merging' fails if another entry is already 'merging' in the same conversation",
          "type": "unit",
          "file": "backend/tests/test_merge_queue_repo.py"
        },
        {
          "id": "TT-110-03",
          "description": "Test list_by_conversation returns entries ordered by position ascending",
          "type": "unit",
          "file": "backend/tests/test_merge_queue_repo.py"
        },
        {
          "id": "TT-110-04",
          "description": "Test assign_reviewer updates the reviewer_agent_id field",
          "type": "unit",
          "file": "backend/tests/test_merge_queue_repo.py"
        }
      ]
    },
    {
      "id": "T-111",
      "title": "JSONL event log: dual-write integration with MessageEvent repository",
      "description": "Extend the existing EventLogWriter/EventLogReader (storage/event_log.py) to integrate with the SQLite MessageEvent repository as a dual-write system. Create a DualWriteMessageEventRepository that wraps SQLiteMessageEventRepository and EventLogWriter: every append() writes to both SQLite and JSONL. Add a conversation_id-scoped log path strategy (already exists as conversation_log_path). Ensure the JSONL log is supplementary \u2014 SQLite is the source of truth, JSONL is for debugging/grep. Acceptance criteria: (1) dual-write wrapper appends to both stores atomically, (2) JSONL contains all fields from the MessageEvent, (3) EventLogReader.read_since works with event_id for SSE reconnection.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R052",
        "BE-R030",
        "BE-R032"
      ],
      "dependencies": [
        "T-108"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/event_log.py",
          "backend/src/agent_orchestrator/storage/repositories/dual_write_message_event.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-events",
      "tests": [
        {
          "id": "TT-111-01",
          "description": "Test DualWriteMessageEventRepository.append writes to both SQLite and JSONL file",
          "type": "integration",
          "file": "backend/tests/test_dual_write_events.py"
        },
        {
          "id": "TT-111-02",
          "description": "Test that JSONL entries contain event_id, conversation_id, source_type, event_type, text, and timestamp",
          "type": "unit",
          "file": "backend/tests/test_dual_write_events.py"
        },
        {
          "id": "TT-111-03",
          "description": "Test EventLogReader.read_since with a known event_id returns only subsequent events",
          "type": "unit",
          "file": "backend/tests/test_dual_write_events.py"
        },
        {
          "id": "TT-111-04",
          "description": "Test that JSONL write failure does not prevent SQLite write (graceful degradation)",
          "type": "unit",
          "file": "backend/tests/test_dual_write_events.py"
        }
      ]
    },
    {
      "id": "T-112",
      "title": "Checkpoint builder: SQLite-backed checkpoint storage",
      "description": "Extend the existing CheckpointBuilder (storage/checkpoint.py) to persist CheckpointPack instances to the artifact table via the ArtifactRepository. Add methods: save(pack) -> Artifact (serializes CheckpointPack to JSON and stores as artifact type='checkpoint'), load_latest(conversation_id) -> CheckpointPack|None (retrieves most recent checkpoint artifact and deserializes). Update conversation.summary_snapshot and latest_artifact_id when a checkpoint is saved. Acceptance criteria: (1) save() persists to artifact table with type='checkpoint', (2) load_latest retrieves and deserializes correctly, (3) conversation metadata updated on save, (4) compact() + save() workflow produces a within-budget checkpoint.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R040",
        "BE-R133"
      ],
      "dependencies": [
        "T-109",
        "T-104"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/storage/checkpoint.py",
          "backend/src/agent_orchestrator/storage/repositories/sqlite_artifact.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/storage/"
        ]
      },
      "complexity": "M",
      "parallel_group": "foundation-events",
      "tests": [
        {
          "id": "TT-112-01",
          "description": "Test save() creates an artifact with type='checkpoint' containing serialized CheckpointPack",
          "type": "integration",
          "file": "backend/tests/test_checkpoint_storage.py"
        },
        {
          "id": "TT-112-02",
          "description": "Test load_latest returns the most recently saved CheckpointPack for a conversation",
          "type": "integration",
          "file": "backend/tests/test_checkpoint_storage.py"
        },
        {
          "id": "TT-112-03",
          "description": "Test save() updates conversation.summary_snapshot and latest_artifact_id",
          "type": "integration",
          "file": "backend/tests/test_checkpoint_storage.py"
        },
        {
          "id": "TT-112-04",
          "description": "Test round-trip: build -> compact -> save -> load_latest produces equivalent CheckpointPack",
          "type": "integration",
          "file": "backend/tests/test_checkpoint_storage.py"
        }
      ]
    },
    {
      "id": "T-113",
      "title": "Configuration management: AppConfig from environment",
      "description": "Create a configuration module at backend/src/agent_orchestrator/config.py that loads settings from environment variables with sensible defaults. Fields: DB_PATH (default: ~/.agent-orchestrator/orchestrator.db), HOST (default: 0.0.0.0), PORT (default: 8000), DEV_MODE (default: false), OLLAMA_URL (default: http://localhost:11434), LOG_DIR (default: ~/.agent-orchestrator/logs/), PERSONALITIES_PATH (default: config/personalities.json). Use a frozen dataclass or Pydantic BaseSettings. Provide a singleton get_config() function. Update db_provider.py to use config for DB_PATH instead of hardcoded :memory:. Acceptance criteria: (1) all config fields loadable from env vars, (2) sensible defaults work when no env vars set, (3) DEV_MODE controls CORS behavior, (4) db_provider uses configured path.",
      "design_refs": [
        "DES-01"
      ],
      "requirements": [
        "BE-R140",
        "BE-R142",
        "BE-R050",
        "BE-R062"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/config.py",
          "backend/src/agent_orchestrator/api/db_provider.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/"
        ]
      },
      "complexity": "S",
      "parallel_group": "foundation-schema",
      "tests": [
        {
          "id": "TT-113-01",
          "description": "Test default config values are used when no environment variables are set",
          "type": "unit",
          "file": "backend/tests/test_config.py"
        },
        {
          "id": "TT-113-02",
          "description": "Test that environment variables override default config values",
          "type": "unit",
          "file": "backend/tests/test_config.py"
        },
        {
          "id": "TT-113-03",
          "description": "Test that DEV_MODE=true is parsed correctly from string env var",
          "type": "unit",
          "file": "backend/tests/test_config.py"
        },
        {
          "id": "TT-113-04",
          "description": "Test that DB_PATH expands ~ to user home directory",
          "type": "unit",
          "file": "backend/tests/test_config.py"
        }
      ]
    },
    {
      "id": "T-114",
      "title": "Personality profiles loader",
      "description": "Create a personality loader module at backend/src/agent_orchestrator/config_loaders/personalities.py that reads config/personalities.json and provides structured access. Define a PersonalityProfile dataclass with fields: key, display_name, system_prompt_fragments (list[str]), temperature (float), behavioral_constraints (list[str]). Provide load_personalities(path?) -> dict[str, PersonalityProfile] and get_personality(key) -> PersonalityProfile|None. Cache loaded profiles (load once on first access). Acceptance criteria: (1) loads from configurable path, (2) returns structured dataclasses, (3) handles missing file gracefully (empty dict), (4) validates required fields.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R141"
      ],
      "dependencies": [
        "T-113"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/config_loaders/__init__.py",
          "backend/src/agent_orchestrator/config_loaders/personalities.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/config_loaders/"
        ]
      },
      "complexity": "S",
      "parallel_group": "foundation-events",
      "tests": [
        {
          "id": "TT-114-01",
          "description": "Test load_personalities parses a valid personalities.json into PersonalityProfile dataclasses",
          "type": "unit",
          "file": "backend/tests/test_personalities_loader.py"
        },
        {
          "id": "TT-114-02",
          "description": "Test load_personalities returns empty dict when file does not exist",
          "type": "unit",
          "file": "backend/tests/test_personalities_loader.py"
        },
        {
          "id": "TT-114-03",
          "description": "Test get_personality returns None for unknown key",
          "type": "unit",
          "file": "backend/tests/test_personalities_loader.py"
        }
      ]
    },
    {
      "id": "T-115",
      "title": "TaskStatus enum alignment with requirements",
      "description": "Update the TaskStatus enum in orchestrator/models.py to match the full status lifecycle from BE-R021: todo, design, tdd, implementing, testing, pr_raised, in_review, fixing_comments, merging, done, blocked. The current enum only has todo, in_progress, blocked, done, failed. Add a VALID_TRANSITIONS dict that defines allowed status transitions (e.g., todo -> design, design -> tdd, etc.). Add a MergeQueueStatus enum for merge queue entries: queued, rebasing, testing, merging, merged, failed, blocked. Add EventType enum: chat_message, debate_turn, phase_change, gate_approval, steer, task_update, system_notice. Acceptance criteria: (1) TaskStatus matches BE-R021, (2) transitions map defined, (3) MergeQueueStatus defined, (4) EventType matches BE-R031.",
      "design_refs": [
        "DES-02"
      ],
      "requirements": [
        "BE-R021",
        "BE-R031",
        "MG-R060"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/models.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "S",
      "parallel_group": "foundation-schema",
      "tests": [
        {
          "id": "TT-115-01",
          "description": "Test TaskStatus enum contains all 11 statuses from BE-R021",
          "type": "unit",
          "file": "backend/tests/test_models_enums.py"
        },
        {
          "id": "TT-115-02",
          "description": "Test VALID_TRANSITIONS allows todo -> design but blocks todo -> implementing",
          "type": "unit",
          "file": "backend/tests/test_models_enums.py"
        },
        {
          "id": "TT-115-03",
          "description": "Test EventType enum contains all 7 event types from BE-R031",
          "type": "unit",
          "file": "backend/tests/test_models_enums.py"
        },
        {
          "id": "TT-115-04",
          "description": "Test MergeQueueStatus enum contains all 7 statuses (queued through blocked)",
          "type": "unit",
          "file": "backend/tests/test_models_enums.py"
        }
      ]
    }
  ],
  "frontend-tasks": [
    {
      "id": "T-301",
      "title": "ChatMessage: message type variants and agent colors",
      "description": "Extend the existing ChatMessage component to support all message types: chat_message, debate_turn, phase_change, system_notice, steer. Add hash-based agent accent colors (HSL from agent ID). Add role badge next to agent name. Add markdown rendering via react-markdown with remark-gfm. Acceptance: each message type renders with distinct styling; agent colors are deterministic; markdown code blocks, lists, bold, and links render correctly.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R010",
        "UI-R011",
        "UI-R012"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/chat/ChatMessage.tsx",
          "frontend/src/features/chat/ChatMessage.css",
          "frontend/src/features/chat/types.ts"
        ],
        "directories": [
          "frontend/src/features/chat/"
        ]
      },
      "complexity": "L",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-301-01",
          "description": "Renders agent message with avatar showing first letter and hash-based color",
          "type": "unit",
          "file": "frontend/src/features/chat/__tests__/ChatMessage.test.tsx"
        },
        {
          "id": "TT-301-02",
          "description": "Renders markdown content (code block, bold, link) via react-markdown",
          "type": "unit",
          "file": "frontend/src/features/chat/__tests__/ChatMessage.test.tsx"
        },
        {
          "id": "TT-301-03",
          "description": "Renders phase_change type as a styled divider with phase label",
          "type": "unit",
          "file": "frontend/src/features/chat/__tests__/ChatMessage.test.tsx"
        },
        {
          "id": "TT-301-04",
          "description": "Renders steer message with highlight border and 'You' sender label",
          "type": "unit",
          "file": "frontend/src/features/chat/__tests__/ChatMessage.test.tsx"
        }
      ]
    },
    {
      "id": "T-302",
      "title": "ChatTimeline: auto-scroll, pagination, new-message badge",
      "description": "Enhance ChatTimeline with smart auto-scroll: auto-scroll when user is at bottom, disable when scrolled up, show floating 'New messages' badge. Add cursor-based pagination (scroll-up loads older messages via ?after= cursor). Acceptance: auto-scroll toggles based on scroll position; badge appears when new messages arrive while scrolled up; clicking badge scrolls to bottom; pagination loads older messages on scroll-up.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R013"
      ],
      "dependencies": [
        "T-301"
      ],
      "scope": {
        "files": [
          "frontend/src/features/chat/ChatTimeline.tsx",
          "frontend/src/features/chat/ChatTimeline.css"
        ],
        "directories": [
          "frontend/src/features/chat/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-302-01",
          "description": "Auto-scrolls to bottom when new message arrives and user is at bottom",
          "type": "unit",
          "file": "frontend/src/features/chat/__tests__/ChatTimeline.test.tsx"
        },
        {
          "id": "TT-302-02",
          "description": "Shows 'New messages' badge when user scrolls up and new message arrives",
          "type": "unit",
          "file": "frontend/src/features/chat/__tests__/ChatTimeline.test.tsx"
        },
        {
          "id": "TT-302-03",
          "description": "Clicking badge scrolls to latest message and hides badge",
          "type": "unit",
          "file": "frontend/src/features/chat/__tests__/ChatTimeline.test.tsx"
        }
      ]
    },
    {
      "id": "T-303",
      "title": "Composer: @mention autocomplete and message routing",
      "description": "Extend the existing Composer to support @mention autocomplete. Typing '@' triggers a dropdown of agents filtered by name. Selecting an agent inserts @AgentName into the text. On send, parse @mentions to set target_agent_id (directed message) or broadcast if no mention. Shift+Enter inserts newline, Enter sends. Acceptance: dropdown appears on '@' keystroke; filtering works; selecting inserts mention; send payload includes target_agent_id when mentioned; broadcast when no mention.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R020",
        "UI-R021",
        "UI-R022"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/composer/Composer.tsx",
          "frontend/src/features/composer/Composer.css",
          "frontend/src/features/composer/types.ts"
        ],
        "directories": [
          "frontend/src/features/composer/"
        ]
      },
      "complexity": "L",
      "parallel_group": "ui-composer",
      "tests": [
        {
          "id": "TT-303-01",
          "description": "Shows autocomplete dropdown when user types '@' with agent list",
          "type": "unit",
          "file": "frontend/src/features/composer/__tests__/Composer.test.tsx"
        },
        {
          "id": "TT-303-02",
          "description": "Filters dropdown as user types after '@' (e.g., '@ri' shows only 'Rick')",
          "type": "unit",
          "file": "frontend/src/features/composer/__tests__/Composer.test.tsx"
        },
        {
          "id": "TT-303-03",
          "description": "Selecting an agent inserts @AgentName and closes dropdown",
          "type": "unit",
          "file": "frontend/src/features/composer/__tests__/Composer.test.tsx"
        },
        {
          "id": "TT-303-04",
          "description": "Send with @mention calls onSend with target_agent_id; send without mention calls with broadcast",
          "type": "unit",
          "file": "frontend/src/features/composer/__tests__/Composer.test.tsx"
        }
      ]
    },
    {
      "id": "T-304",
      "title": "PhaseBanner: sticky debate phase indicator",
      "description": "Create a PhaseBanner component that shows the current phase name, round counter (e.g., 'Debate -- Round 5/20'), and a speaking indicator when an agent is generating a response. Sticky-positioned at top of ChatPane. Acceptance: banner shows phase name and round; speaking indicator shows agent name and animated dots; banner is sticky and visible while scrolling chat.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R030"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/debate/PhaseBanner.tsx",
          "frontend/src/features/debate/PhaseBanner.css",
          "frontend/src/features/debate/types.ts"
        ],
        "directories": [
          "frontend/src/features/debate/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-debate",
      "tests": [
        {
          "id": "TT-304-01",
          "description": "Renders phase name and round counter (e.g., 'Debate -- Round 5/20')",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/PhaseBanner.test.tsx"
        },
        {
          "id": "TT-304-02",
          "description": "Shows speaking indicator with agent name when an agent is generating",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/PhaseBanner.test.tsx"
        },
        {
          "id": "TT-304-03",
          "description": "Hides speaking indicator when no agent is speaking",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/PhaseBanner.test.tsx"
        }
      ]
    },
    {
      "id": "T-305",
      "title": "ClarificationBanner: agent needs-input notification",
      "description": "Create a ClarificationBanner component that appears when an agent @mentions the customer for clarification. Amber banner with 'Agent X needs your input' text and a 'View Question' button that scrolls to the relevant message. Acceptance: banner appears with correct agent name; clicking 'View Question' scrolls chat to the message; banner is dismissible.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R031"
      ],
      "dependencies": [
        "T-304"
      ],
      "scope": {
        "files": [
          "frontend/src/features/debate/ClarificationBanner.tsx",
          "frontend/src/features/debate/ClarificationBanner.css"
        ],
        "directories": [
          "frontend/src/features/debate/"
        ]
      },
      "complexity": "S",
      "parallel_group": "ui-debate",
      "tests": [
        {
          "id": "TT-305-01",
          "description": "Renders amber banner with agent name when clarification is needed",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/ClarificationBanner.test.tsx"
        },
        {
          "id": "TT-305-02",
          "description": "Clicking 'View Question' calls scrollToMessage callback with message ID",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/ClarificationBanner.test.tsx"
        },
        {
          "id": "TT-305-03",
          "description": "Banner is dismissible and does not render when no clarification is pending",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/ClarificationBanner.test.tsx"
        }
      ]
    },
    {
      "id": "T-306",
      "title": "GateControls: approve, steer, decide buttons",
      "description": "Create a GateControls component with three customer action buttons: 'Approve & Advance' (approves current agreement, triggers phase transition), 'Steer' (focuses the composer for steering input), 'Decide' (ends debate, lets customer pick direction). Buttons call respective API actions (gate_approval event). Acceptance: three buttons render during debate phase; Approve calls gate approval API; Steer focuses composer; Decide opens decision modal/prompt.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R032"
      ],
      "dependencies": [
        "T-304"
      ],
      "scope": {
        "files": [
          "frontend/src/features/debate/GateControls.tsx",
          "frontend/src/features/debate/GateControls.css"
        ],
        "directories": [
          "frontend/src/features/debate/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-debate",
      "tests": [
        {
          "id": "TT-306-01",
          "description": "Renders Approve, Steer, and Decide buttons",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/GateControls.test.tsx"
        },
        {
          "id": "TT-306-02",
          "description": "Clicking Approve calls onApprove callback",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/GateControls.test.tsx"
        },
        {
          "id": "TT-306-03",
          "description": "Clicking Steer calls onSteer callback to focus composer",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/GateControls.test.tsx"
        },
        {
          "id": "TT-306-04",
          "description": "Clicking Decide calls onDecide callback",
          "type": "unit",
          "file": "frontend/src/features/debate/__tests__/GateControls.test.tsx"
        }
      ]
    },
    {
      "id": "T-307",
      "title": "KanbanBoard: dashboard columns and horizontal scroll",
      "description": "Create a KanbanBoard component with columns for each task status: Todo, Design, TDD, Implementing, Testing, PR Raised, In Review, Fixing Comments, Merging, Done. Columns scroll horizontally. Each column header shows task count. Empty columns are shown but dimmed. Acceptance: all 10 columns render; task count in headers; horizontal scroll works; empty columns are visually dimmed.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R050"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/dashboard/KanbanBoard.tsx",
          "frontend/src/features/dashboard/KanbanBoard.css",
          "frontend/src/features/dashboard/types.ts"
        ],
        "directories": [
          "frontend/src/features/dashboard/"
        ]
      },
      "complexity": "L",
      "parallel_group": "ui-dashboard",
      "tests": [
        {
          "id": "TT-307-01",
          "description": "Renders all 10 status columns with correct headers",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/KanbanBoard.test.tsx"
        },
        {
          "id": "TT-307-02",
          "description": "Shows task count in each column header",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/KanbanBoard.test.tsx"
        },
        {
          "id": "TT-307-03",
          "description": "Empty columns have dimmed styling",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/KanbanBoard.test.tsx"
        },
        {
          "id": "TT-307-04",
          "description": "Tasks render in the correct column based on status",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/KanbanBoard.test.tsx"
        }
      ]
    },
    {
      "id": "T-308",
      "title": "TaskCard: dashboard task card component",
      "description": "Create a TaskCard component displaying: task title (truncated with tooltip), agent badge (avatar + name, color-coded), PR link (clickable PR number), reviewer badge, and left-border accent color matching column status. Clicking opens TaskDetailModal. Acceptance: title truncates with tooltip; agent badge shows with color; PR link opens in new tab; status accent border is correct.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R051"
      ],
      "dependencies": [
        "T-307"
      ],
      "scope": {
        "files": [
          "frontend/src/features/dashboard/TaskCard.tsx",
          "frontend/src/features/dashboard/TaskCard.css"
        ],
        "directories": [
          "frontend/src/features/dashboard/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-dashboard",
      "tests": [
        {
          "id": "TT-308-01",
          "description": "Renders task title, agent badge, and status accent border",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskCard.test.tsx"
        },
        {
          "id": "TT-308-02",
          "description": "Long title is truncated with tooltip showing full text",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskCard.test.tsx"
        },
        {
          "id": "TT-308-03",
          "description": "PR link renders as clickable link opening in new tab when PR exists",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskCard.test.tsx"
        },
        {
          "id": "TT-308-04",
          "description": "Clicking card calls onClick handler with task ID",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskCard.test.tsx"
        }
      ]
    },
    {
      "id": "T-309",
      "title": "TaskDetailModal: task detail overlay",
      "description": "Create a TaskDetailModal component as a modal overlay showing: header (title, status badge, priority badge), description (markdown-rendered), scope (file list), dependencies (with status indicators), assigned agent (link to activity viewer), PR status (number, URL, CI status, review status, merge queue position), and activity log (filtered timeline). Read-only. Acceptance: modal opens with full task details; markdown description renders; dependencies show status; PR section shows all fields; modal closes on overlay click or X button.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R054"
      ],
      "dependencies": [
        "T-308"
      ],
      "scope": {
        "files": [
          "frontend/src/features/dashboard/TaskDetailModal.tsx",
          "frontend/src/features/dashboard/TaskDetailModal.css"
        ],
        "directories": [
          "frontend/src/features/dashboard/"
        ]
      },
      "complexity": "L",
      "parallel_group": "ui-dashboard",
      "tests": [
        {
          "id": "TT-309-01",
          "description": "Renders task title, status badge, and priority in header",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskDetailModal.test.tsx"
        },
        {
          "id": "TT-309-02",
          "description": "Renders markdown description with code blocks and lists",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskDetailModal.test.tsx"
        },
        {
          "id": "TT-309-03",
          "description": "Shows dependencies with their current status indicators",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskDetailModal.test.tsx"
        },
        {
          "id": "TT-309-04",
          "description": "Closes modal when overlay is clicked or X button is pressed",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/TaskDetailModal.test.tsx"
        }
      ]
    },
    {
      "id": "T-310",
      "title": "AgentStatusBar: compact agent status strip",
      "description": "Create an AgentStatusBar component that shows a compact strip below/above the Kanban board with each agent's current state: status dot (green=idle, blue=running, amber=blocked, gray=offline), agent name, provider, and current task title. Clicking an agent opens their activity viewer. Acceptance: all agents render with correct status dot colors; current task shows when assigned; clicking agent calls onSelectAgent.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R052"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/dashboard/AgentStatusBar.tsx",
          "frontend/src/features/dashboard/AgentStatusBar.css"
        ],
        "directories": [
          "frontend/src/features/dashboard/"
        ]
      },
      "complexity": "S",
      "parallel_group": "ui-dashboard",
      "tests": [
        {
          "id": "TT-310-01",
          "description": "Renders all agents with name, provider, and status dot",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/AgentStatusBar.test.tsx"
        },
        {
          "id": "TT-310-02",
          "description": "Status dot has correct color class for each status (idle=green, running=blue, blocked=amber, offline=gray)",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/AgentStatusBar.test.tsx"
        },
        {
          "id": "TT-310-03",
          "description": "Shows current task title when agent has an assigned task",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/AgentStatusBar.test.tsx"
        },
        {
          "id": "TT-310-04",
          "description": "Clicking an agent row calls onSelectAgent with agent ID",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/AgentStatusBar.test.tsx"
        }
      ]
    },
    {
      "id": "T-311",
      "title": "MergeQueue: merge queue display panel",
      "description": "Create a MergeQueue component showing an ordered list of PRs waiting to merge. Each entry shows: position number, status icon (waiting/rebasing/testing/merging), PR number, task title, author agent, and current status text. The currently-merging PR is highlighted. Acceptance: entries render in order; status icons match state; active PR is highlighted; empty state shows 'No PRs in queue'.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R053"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/dashboard/MergeQueue.tsx",
          "frontend/src/features/dashboard/MergeQueue.css"
        ],
        "directories": [
          "frontend/src/features/dashboard/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-dashboard",
      "tests": [
        {
          "id": "TT-311-01",
          "description": "Renders merge queue entries in order with position, PR number, and task title",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/MergeQueue.test.tsx"
        },
        {
          "id": "TT-311-02",
          "description": "Currently-merging PR has highlighted styling",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/MergeQueue.test.tsx"
        },
        {
          "id": "TT-311-03",
          "description": "Shows 'No PRs in queue' when list is empty",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/MergeQueue.test.tsx"
        }
      ]
    },
    {
      "id": "T-312",
      "title": "AgentRoster: enhanced roster with status, task, and activity viewer toggle",
      "description": "Enhance the existing AgentRoster and AgentCard to show: role badge (Analyst/Team Lead/Developer), provider icon, status dot (green/blue/amber/gray), and current task title if assigned. Clicking an agent opens their activity viewer in the right pane (replacing the roster). Add 'Back to Roster' navigation. Acceptance: agent cards show role, provider icon, status, and current task; clicking opens activity viewer; back button returns to roster.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R060",
        "UI-R061"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/agents/AgentRoster.tsx",
          "frontend/src/features/agents/AgentCard.tsx",
          "frontend/src/features/agents/AgentCard.css",
          "frontend/src/features/agents/AgentRoster.css",
          "frontend/src/features/agents/types.ts"
        ],
        "directories": [
          "frontend/src/features/agents/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-312-01",
          "description": "Agent card shows role badge, provider icon, status dot, and current task",
          "type": "unit",
          "file": "frontend/src/features/agents/__tests__/AgentCard.test.tsx"
        },
        {
          "id": "TT-312-02",
          "description": "Clicking agent card calls onSelectAgent to open activity viewer",
          "type": "unit",
          "file": "frontend/src/features/agents/__tests__/AgentRoster.test.tsx"
        },
        {
          "id": "TT-312-03",
          "description": "Back to Roster button calls onBackToRoster callback",
          "type": "unit",
          "file": "frontend/src/features/agents/__tests__/AgentRoster.test.tsx"
        }
      ]
    },
    {
      "id": "T-313",
      "title": "Add/Remove agent form in roster",
      "description": "Enhance the existing agent editor to work as a proper form within the roster panel. Add agent form collects: name, role, provider, model selection. Remove agent button detaches agent from conversation. Acceptance: form validates required fields; create calls API and adds agent to roster; remove calls API and removes from roster; form closes on save/cancel.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R062"
      ],
      "dependencies": [
        "T-312"
      ],
      "scope": {
        "files": [
          "frontend/src/features/agents/AgentForm.tsx",
          "frontend/src/features/agents/AgentForm.css"
        ],
        "directories": [
          "frontend/src/features/agents/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-313-01",
          "description": "Add agent form renders name, role, provider, and model fields",
          "type": "unit",
          "file": "frontend/src/features/agents/__tests__/AgentForm.test.tsx"
        },
        {
          "id": "TT-313-02",
          "description": "Form validates that name and model are required before submit",
          "type": "unit",
          "file": "frontend/src/features/agents/__tests__/AgentForm.test.tsx"
        },
        {
          "id": "TT-313-03",
          "description": "Submitting calls onSave with form data; cancel calls onCancel",
          "type": "unit",
          "file": "frontend/src/features/agents/__tests__/AgentForm.test.tsx"
        }
      ]
    },
    {
      "id": "T-314",
      "title": "ActivityViewer: terminal-like agent activity stream",
      "description": "Create an ActivityViewer component with terminal aesthetic (dark background, monospace font, green/amber text). Renders event types: thinking (dimmed italic), text (normal), tool_call (highlighted with tool name badge), tool_result (indented), file_edit (filename + diff), shell_command (command + output), error (red text). Auto-scroll to bottom with 'Resume' button when scrolled up. Replaces roster in right pane when active. Acceptance: terminal styling applied; all event types render distinctly; auto-scroll works with resume button; back button returns to roster.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R040",
        "UI-R041",
        "UI-R042",
        "UI-R043"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/activity/ActivityViewer.tsx",
          "frontend/src/features/activity/ActivityViewer.css",
          "frontend/src/features/activity/types.ts",
          "frontend/src/features/activity/ActivityEvent.tsx"
        ],
        "directories": [
          "frontend/src/features/activity/"
        ]
      },
      "complexity": "L",
      "parallel_group": "ui-activity",
      "tests": [
        {
          "id": "TT-314-01",
          "description": "Renders with terminal aesthetic: dark background, monospace font",
          "type": "unit",
          "file": "frontend/src/features/activity/__tests__/ActivityViewer.test.tsx"
        },
        {
          "id": "TT-314-02",
          "description": "Renders thinking event as dimmed italic text",
          "type": "unit",
          "file": "frontend/src/features/activity/__tests__/ActivityViewer.test.tsx"
        },
        {
          "id": "TT-314-03",
          "description": "Renders tool_call event with highlighted tool name badge and tool_result indented below",
          "type": "unit",
          "file": "frontend/src/features/activity/__tests__/ActivityViewer.test.tsx"
        },
        {
          "id": "TT-314-04",
          "description": "Shows Resume button when user scrolls up; clicking it re-enables auto-scroll",
          "type": "unit",
          "file": "frontend/src/features/activity/__tests__/ActivityViewer.test.tsx"
        }
      ]
    },
    {
      "id": "T-315",
      "title": "ViewSwitcher: Chat/Dashboard toggle in center pane",
      "description": "Add a view toggle to the TopBar or center pane that switches the main content between ChatPane and DashboardPane (KanbanBoard). The sidebar (HistoryPane) and right pane (IntelligencePane/Roster) persist across views. Acceptance: toggle renders with Chat and Dashboard options; switching shows the correct pane; current view is visually indicated; sidebar and right pane remain visible.",
      "design_refs": [
        "DES-03",
        "DES-04"
      ],
      "requirements": [
        "UI-R001",
        "UI-R002"
      ],
      "dependencies": [
        "T-307"
      ],
      "scope": {
        "files": [
          "frontend/src/layout/TopBar.tsx",
          "frontend/src/layout/TopBar.css",
          "frontend/src/layout/ChatPane.tsx",
          "frontend/src/layout/AppShell.tsx"
        ],
        "directories": [
          "frontend/src/layout/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-315-01",
          "description": "Renders Chat and Dashboard toggle buttons in TopBar",
          "type": "unit",
          "file": "frontend/src/layout/__tests__/TopBar.test.tsx"
        },
        {
          "id": "TT-315-02",
          "description": "Clicking Dashboard shows KanbanBoard in center pane",
          "type": "integration",
          "file": "frontend/src/layout/__tests__/AppShell.test.tsx"
        },
        {
          "id": "TT-315-03",
          "description": "Clicking Chat returns to ChatPane with messages preserved",
          "type": "integration",
          "file": "frontend/src/layout/__tests__/AppShell.test.tsx"
        }
      ]
    },
    {
      "id": "T-316",
      "title": "ConversationSidebar: conversation list with create/switch/delete",
      "description": "Enhance the existing HistoryPane to fully implement the conversation sidebar: sorted by updated_at DESC, each entry shows title + phase badge + relative time, create button opens dialog for title + project directory, active conversation highlighted, click to switch (calls /conversations/select), right-click context menu for delete. Acceptance: conversations sorted by recency; phase badge shows; create dialog works; active highlight; context menu delete.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R070",
        "UI-R071",
        "UI-R072"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/layout/HistoryPane.tsx",
          "frontend/src/features/history/ConversationItem.tsx",
          "frontend/src/features/history/ConversationList.tsx",
          "frontend/src/features/history/types.ts"
        ],
        "directories": [
          "frontend/src/features/history/",
          "frontend/src/layout/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-316-01",
          "description": "Renders conversations sorted by updated_at descending",
          "type": "unit",
          "file": "frontend/src/features/history/__tests__/ConversationList.test.tsx"
        },
        {
          "id": "TT-316-02",
          "description": "Active conversation has highlighted styling",
          "type": "unit",
          "file": "frontend/src/features/history/__tests__/ConversationItem.test.tsx"
        },
        {
          "id": "TT-316-03",
          "description": "Clicking create opens dialog; submitting creates conversation",
          "type": "integration",
          "file": "frontend/src/features/history/__tests__/ConversationList.test.tsx"
        },
        {
          "id": "TT-316-04",
          "description": "Right-click shows context menu with delete option",
          "type": "unit",
          "file": "frontend/src/features/history/__tests__/ConversationItem.test.tsx"
        }
      ]
    },
    {
      "id": "T-317",
      "title": "ToastNotification: in-app notification system",
      "description": "Create a ToastNotification system with a NotificationProvider context and useNotification hook. Toast types: clarification (amber), max_rounds (warning/yellow), pr_ready (info/blue), agent_blocked (alert/red). Toasts appear in top-right corner, auto-dismiss after 8 seconds, and are clickable (navigate to relevant context). Acceptance: toasts render in top-right; auto-dismiss after 8s; click navigates; correct color per type; multiple toasts stack.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R080",
        "UI-R081"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/features/notifications/ToastNotification.tsx",
          "frontend/src/features/notifications/ToastNotification.css",
          "frontend/src/features/notifications/NotificationProvider.tsx",
          "frontend/src/features/notifications/useNotification.ts",
          "frontend/src/features/notifications/types.ts"
        ],
        "directories": [
          "frontend/src/features/notifications/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-activity",
      "tests": [
        {
          "id": "TT-317-01",
          "description": "Renders toast with correct color styling based on notification type",
          "type": "unit",
          "file": "frontend/src/features/notifications/__tests__/ToastNotification.test.tsx"
        },
        {
          "id": "TT-317-02",
          "description": "Toast auto-dismisses after 8 seconds",
          "type": "unit",
          "file": "frontend/src/features/notifications/__tests__/ToastNotification.test.tsx"
        },
        {
          "id": "TT-317-03",
          "description": "Clicking toast calls onClick handler for navigation",
          "type": "unit",
          "file": "frontend/src/features/notifications/__tests__/ToastNotification.test.tsx"
        },
        {
          "id": "TT-317-04",
          "description": "Multiple toasts stack vertically in top-right corner",
          "type": "unit",
          "file": "frontend/src/features/notifications/__tests__/ToastNotification.test.tsx"
        }
      ]
    },
    {
      "id": "T-318",
      "title": "useSSE: SSE hook for real-time event streaming",
      "description": "Create a useSSE custom hook that connects to an SSE endpoint, parses events, handles reconnection with Last-Event-ID, and exposes events via state. Hook accepts URL and optional event type filters. Handles connection lifecycle (open, error, reconnect). Used by ActivityViewer and notification system. Acceptance: connects to SSE endpoint; parses event data; reconnects on error with Last-Event-ID; exposes events array and connection status; cleanup on unmount.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R040"
      ],
      "dependencies": [],
      "scope": {
        "files": [
          "frontend/src/hooks/useSSE.ts",
          "frontend/src/hooks/types.ts"
        ],
        "directories": [
          "frontend/src/hooks/"
        ]
      },
      "complexity": "L",
      "parallel_group": "ui-activity",
      "tests": [
        {
          "id": "TT-318-01",
          "description": "Connects to SSE endpoint and receives parsed events",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useSSE.test.ts"
        },
        {
          "id": "TT-318-02",
          "description": "Reconnects with Last-Event-ID header after connection error",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useSSE.test.ts"
        },
        {
          "id": "TT-318-03",
          "description": "Closes EventSource on component unmount (cleanup)",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useSSE.test.ts"
        },
        {
          "id": "TT-318-04",
          "description": "Exposes connection status (connecting, open, closed, error)",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useSSE.test.ts"
        }
      ]
    },
    {
      "id": "T-319",
      "title": "useConversationMessages: real-time message hook with SSE",
      "description": "Create a useConversationMessages hook that combines initial message fetch (GET /api/conversations/{id}/messages) with SSE streaming for new messages. Merges API messages with SSE events. Handles conversation switching (cleanup old SSE, start new). Acceptance: fetches initial messages on mount; merges SSE messages in real-time; switches SSE connection on conversation change; deduplicates messages by ID.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R010",
        "UI-R013"
      ],
      "dependencies": [
        "T-318"
      ],
      "scope": {
        "files": [
          "frontend/src/hooks/useConversationMessages.ts"
        ],
        "directories": [
          "frontend/src/hooks/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-activity",
      "tests": [
        {
          "id": "TT-319-01",
          "description": "Fetches initial messages from API on mount",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useConversationMessages.test.ts"
        },
        {
          "id": "TT-319-02",
          "description": "Appends new messages from SSE stream in real-time",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useConversationMessages.test.ts"
        },
        {
          "id": "TT-319-03",
          "description": "Deduplicates messages by ID when SSE delivers already-fetched messages",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useConversationMessages.test.ts"
        }
      ]
    },
    {
      "id": "T-320",
      "title": "useAgentActivity: SSE hook for per-agent activity stream",
      "description": "Create a useAgentActivity hook that connects to GET /api/agents/{id}/activity SSE endpoint and streams activity events (thinking, text, tool_call, tool_result, file_edit, shell_command, error). Exposes events array, connection status, and clear function. Accepts agent ID and auto-connects when non-null. Acceptance: connects to agent activity SSE; parses typed events; auto-disconnects when agent ID changes; clears events on agent switch.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R040",
        "UI-R042"
      ],
      "dependencies": [
        "T-318"
      ],
      "scope": {
        "files": [
          "frontend/src/hooks/useAgentActivity.ts"
        ],
        "directories": [
          "frontend/src/hooks/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-activity",
      "tests": [
        {
          "id": "TT-320-01",
          "description": "Connects to agent activity SSE endpoint when agent ID is provided",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useAgentActivity.test.ts"
        },
        {
          "id": "TT-320-02",
          "description": "Parses typed activity events (thinking, tool_call, error)",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useAgentActivity.test.ts"
        },
        {
          "id": "TT-320-03",
          "description": "Disconnects and clears events when agent ID changes",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useAgentActivity.test.ts"
        }
      ]
    },
    {
      "id": "T-321",
      "title": "useNotifications: SSE-driven notification hook",
      "description": "Create a useNotifications hook that listens to the conversation SSE stream for notification-triggering events (agent @mention of customer, max_rounds reached, PR ready, agent blocked). Dispatches notifications via the NotificationProvider context. Acceptance: detects @mention events and dispatches clarification notification; detects max_rounds and dispatches warning; detects PR ready and dispatches info; integrates with ToastNotification system.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R080",
        "UI-R031"
      ],
      "dependencies": [
        "T-317",
        "T-318"
      ],
      "scope": {
        "files": [
          "frontend/src/hooks/useNotifications.ts"
        ],
        "directories": [
          "frontend/src/hooks/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-activity",
      "tests": [
        {
          "id": "TT-321-01",
          "description": "Dispatches clarification notification when agent @mentions customer",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useNotifications.test.ts"
        },
        {
          "id": "TT-321-02",
          "description": "Dispatches warning notification when max_rounds is reached",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useNotifications.test.ts"
        },
        {
          "id": "TT-321-03",
          "description": "Dispatches info notification when PR is ready",
          "type": "unit",
          "file": "frontend/src/hooks/__tests__/useNotifications.test.ts"
        }
      ]
    },
    {
      "id": "T-322",
      "title": "RightPane state machine: roster vs activity viewer toggle",
      "description": "Implement the right pane state management in IntelligencePane to toggle between AgentRoster view and ActivityViewer view. Clicking an agent in roster switches to ActivityViewer for that agent. 'Back to Roster' button returns to roster. When in dashboard mode, right pane shows activity viewer or agent status. Acceptance: right pane defaults to roster; clicking agent switches to activity viewer; back button returns to roster; selected agent ID is passed to activity viewer.",
      "design_refs": [
        "DES-03",
        "DES-04"
      ],
      "requirements": [
        "UI-R041",
        "UI-R061"
      ],
      "dependencies": [
        "T-312",
        "T-314"
      ],
      "scope": {
        "files": [
          "frontend/src/layout/IntelligencePane.tsx",
          "frontend/src/layout/IntelligencePane.css"
        ],
        "directories": [
          "frontend/src/layout/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-322-01",
          "description": "Defaults to showing AgentRoster in right pane",
          "type": "unit",
          "file": "frontend/src/layout/__tests__/IntelligencePane.test.tsx"
        },
        {
          "id": "TT-322-02",
          "description": "Switches to ActivityViewer when an agent is selected",
          "type": "integration",
          "file": "frontend/src/layout/__tests__/IntelligencePane.test.tsx"
        },
        {
          "id": "TT-322-03",
          "description": "Back to Roster button returns to roster view",
          "type": "integration",
          "file": "frontend/src/layout/__tests__/IntelligencePane.test.tsx"
        }
      ]
    },
    {
      "id": "T-323",
      "title": "DashboardPane: integrated dashboard with Kanban, status bar, merge queue",
      "description": "Create a DashboardPane component that composes KanbanBoard, AgentStatusBar, and MergeQueue into the center pane layout. Fetches task data and passes to children. Handles task card click to open TaskDetailModal. Acceptance: all three sub-components render; task data flows correctly; clicking card opens modal; layout is responsive with horizontal scroll for Kanban.",
      "design_refs": [
        "DES-04"
      ],
      "requirements": [
        "UI-R050",
        "UI-R052",
        "UI-R053"
      ],
      "dependencies": [
        "T-307",
        "T-310",
        "T-311"
      ],
      "scope": {
        "files": [
          "frontend/src/features/dashboard/DashboardPane.tsx",
          "frontend/src/features/dashboard/DashboardPane.css"
        ],
        "directories": [
          "frontend/src/features/dashboard/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-dashboard",
      "tests": [
        {
          "id": "TT-323-01",
          "description": "Renders KanbanBoard, AgentStatusBar, and MergeQueue sections",
          "type": "integration",
          "file": "frontend/src/features/dashboard/__tests__/DashboardPane.test.tsx"
        },
        {
          "id": "TT-323-02",
          "description": "Opens TaskDetailModal when a task card is clicked",
          "type": "integration",
          "file": "frontend/src/features/dashboard/__tests__/DashboardPane.test.tsx"
        },
        {
          "id": "TT-323-03",
          "description": "Renders empty state when no tasks exist",
          "type": "unit",
          "file": "frontend/src/features/dashboard/__tests__/DashboardPane.test.tsx"
        }
      ]
    },
    {
      "id": "T-324",
      "title": "Responsive layout: desktop-first with mobile fallback",
      "description": "Add responsive CSS and layout adjustments to make the four-zone layout work on desktop browsers (P0) with a reasonable fallback on tablet/phone. On narrow screens: collapse sidebar to icon-only, stack right pane below chat, and make Kanban scroll vertically. Acceptance: layout is usable at 1280px+ (desktop); sidebar collapses at <1024px; right pane stacks below at <768px; no horizontal overflow at any breakpoint.",
      "design_refs": [
        "DES-03"
      ],
      "requirements": [
        "UI-R003"
      ],
      "dependencies": [
        "T-315"
      ],
      "scope": {
        "files": [
          "frontend/src/layout/AppShell.css",
          "frontend/src/layout/HistoryPane.css"
        ],
        "directories": [
          "frontend/src/layout/"
        ]
      },
      "complexity": "M",
      "parallel_group": "ui-chat",
      "tests": [
        {
          "id": "TT-324-01",
          "description": "Four-zone layout renders correctly at 1280px viewport width",
          "type": "integration",
          "file": "frontend/src/layout/__tests__/AppShell.responsive.test.tsx"
        },
        {
          "id": "TT-324-02",
          "description": "Sidebar collapses to icon-only at <1024px viewport",
          "type": "integration",
          "file": "frontend/src/layout/__tests__/AppShell.responsive.test.tsx"
        },
        {
          "id": "TT-324-03",
          "description": "No horizontal overflow at 768px viewport width",
          "type": "integration",
          "file": "frontend/src/layout/__tests__/AppShell.responsive.test.tsx"
        }
      ]
    }
  ],
  "orchestration-tasks": [
    {
      "id": "T-401",
      "title": "Debate engine turn state tracker",
      "description": "Implement the DebateState dataclass and DebateEngine class that tracks current_round, current_turn_index, max_rounds, and paused status. The engine must cycle through agents by turn_order from conversation_agent records, increment rounds when all agents have spoken, and stop at max_rounds. Acceptance criteria: (1) DebateState tracks round/turn/pause state, (2) advance_turn() correctly cycles through agents and increments rounds, (3) is_complete() returns true when max_rounds exceeded.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R001",
        "OR-R002"
      ],
      "dependencies": [
        "T-101",
        "T-102"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/debate.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-401-01",
          "description": "Round-robin cycles through all agents in turn_order, then increments round",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-401-02",
          "description": "Skips disabled agents (enabled=0) in the rotation",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-401-03",
          "description": "is_complete() returns true after max_rounds rounds",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-401-04",
          "description": "State correctly resets when starting a new debate session",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        }
      ]
    },
    {
      "id": "T-402",
      "title": "Customer message injection in debate",
      "description": "Implement customer-as-participant: when the customer sends a message during a debate, it is stored as a chat_message event and made visible to all agents on their next turn. Customer messages do not consume a turn slot in the round-robin. Acceptance criteria: (1) customer messages are injected into agent context without taking a turn, (2) all agents see customer messages on their next turn, (3) multiple customer messages between turns are all included.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R003"
      ],
      "dependencies": [
        "T-401"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/debate.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "S",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-402-01",
          "description": "Customer message appears in all agents' context on their next turn",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-402-02",
          "description": "Customer message does not advance the turn counter or round",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-402-03",
          "description": "Multiple customer messages between turns are all preserved in order",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        }
      ]
    },
    {
      "id": "T-403",
      "title": "Directed message interrupt-and-resume",
      "description": "When the customer addresses a specific agent via @mention, the targeted agent gets an immediate out-of-order turn. After the targeted agent responds, the round-robin resumes from the interrupted position (not from the beginning). Acceptance criteria: (1) @mention detection sets target_agent_id in message metadata, (2) targeted agent gets next turn immediately, (3) round-robin resumes from interrupted position, (4) no agent is skipped or gets an extra turn.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R010"
      ],
      "dependencies": [
        "T-401"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/debate.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-403-01",
          "description": "Directed message gives targeted agent immediate next turn",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-403-02",
          "description": "Round-robin resumes from interrupted position after directed turn",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-403-03",
          "description": "Directed message mid-round does not cause any agent to be skipped",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        }
      ]
    },
    {
      "id": "T-404",
      "title": "Clarification pause on agent @Customer mention",
      "description": "When an agent's response contains @Customer (or a structured marker), the debate engine pauses (paused=true), emits a clarification_needed event, and stops cycling until the customer responds. When the customer responds, paused is set to false and the next agent in turn order proceeds. Acceptance criteria: (1) @Customer detection in agent response triggers pause, (2) clarification_needed event is emitted, (3) debate stops cycling while paused, (4) customer response resumes debate from correct position.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R011"
      ],
      "dependencies": [
        "T-401",
        "T-402"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/debate.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-404-01",
          "description": "Agent response with @Customer triggers paused state and clarification_needed event",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-404-02",
          "description": "No turns are dispatched while debate is paused",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-404-03",
          "description": "Customer response unpauses debate and next agent in order proceeds",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        }
      ]
    },
    {
      "id": "T-405",
      "title": "Agreement detection (structured + text)",
      "description": "Implement dual agreement detection: (1) parse structured JSON markers ({\"agreement\": {\"option\": ..., \"confidence\": ...}}) from agent responses, (2) fallback text analysis for phrases like 'I agree with option X'. When all agents agree on the same option, emit a system_notice and set gate_status to pending_approval. Agreement does NOT auto-advance phases. Acceptance criteria: (1) structured JSON agreement markers are parsed, (2) text-based agreement phrases are detected, (3) unanimous agreement triggers system_notice and pending_approval gate, (4) partial agreement is tracked but does not trigger gate.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R020"
      ],
      "dependencies": [
        "T-401"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/agreement.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-405-01",
          "description": "Structured JSON agreement marker is parsed correctly from agent response",
          "type": "unit",
          "file": "backend/tests/test_agreement.py"
        },
        {
          "id": "TT-405-02",
          "description": "Text-based agreement phrases are detected as fallback",
          "type": "unit",
          "file": "backend/tests/test_agreement.py"
        },
        {
          "id": "TT-405-03",
          "description": "Unanimous agreement emits system_notice and sets gate to pending_approval",
          "type": "unit",
          "file": "backend/tests/test_agreement.py"
        },
        {
          "id": "TT-405-04",
          "description": "Partial agreement (2/3 agents) does not trigger gate change",
          "type": "unit",
          "file": "backend/tests/test_agreement.py"
        }
      ]
    },
    {
      "id": "T-406",
      "title": "Auto-summary after max rounds",
      "description": "When the debate reaches max_rounds without agreement, send each agent a final prompt requesting a structured summary (position, pros, cons, recommendation). Collect all summaries, emit a system_notice with a formatted comparison, and set gate_status to pending_approval. Acceptance criteria: (1) max_rounds triggers summary prompt to all agents, (2) structured summary format is enforced, (3) comparison is formatted and emitted as system_notice, (4) gate_status set to pending_approval.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R021",
        "OR-R002"
      ],
      "dependencies": [
        "T-401",
        "T-405"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/debate.py",
          "backend/src/agent_orchestrator/orchestrator/agreement.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-406-01",
          "description": "Reaching max_rounds sends summary prompt to all agents",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-406-02",
          "description": "Structured summary responses are collected and formatted into comparison",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        },
        {
          "id": "TT-406-03",
          "description": "System notice with comparison is emitted and gate set to pending_approval",
          "type": "unit",
          "file": "backend/tests/test_debate_engine.py"
        }
      ]
    },
    {
      "id": "T-407",
      "title": "Debate context builder",
      "description": "Build the context payload sent to each agent on their debate turn: conversation_id, phase, round number, max_rounds, agent role/name, conversation history, customer_messages_since_your_last_turn, and system_prompt. Acceptance criteria: (1) context includes all required fields per DES-05, (2) customer messages since agent's last turn are isolated correctly, (3) system prompt is generated based on agent role and debate phase.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R030"
      ],
      "dependencies": [
        "T-401",
        "T-402"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/context.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-407-01",
          "description": "Context payload includes all required fields (conversation_id, phase, round, etc.)",
          "type": "unit",
          "file": "backend/tests/test_context_builder.py"
        },
        {
          "id": "TT-407-02",
          "description": "customer_messages_since_your_last_turn returns only messages after agent's last turn",
          "type": "unit",
          "file": "backend/tests/test_context_builder.py"
        },
        {
          "id": "TT-407-03",
          "description": "System prompt varies correctly based on agent role",
          "type": "unit",
          "file": "backend/tests/test_context_builder.py"
        }
      ]
    },
    {
      "id": "T-408",
      "title": "Context windowing and rolling summary",
      "description": "When conversation history exceeds a configurable token threshold (default ~100K tokens), create a rolling summary checkpoint using Ollama (free). Agents receive: summary + last N messages instead of full history. Acceptance criteria: (1) token count estimation for history, (2) threshold triggers summary generation via Ollama, (3) agents receive summary + recent messages, (4) summary is stored as a checkpoint artifact.",
      "design_refs": [
        "DES-05"
      ],
      "requirements": [
        "OR-R031"
      ],
      "dependencies": [
        "T-407",
        "T-601"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/context.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-debate",
      "tests": [
        {
          "id": "TT-408-01",
          "description": "History below token threshold returns full history unchanged",
          "type": "unit",
          "file": "backend/tests/test_context_builder.py"
        },
        {
          "id": "TT-408-02",
          "description": "History above threshold triggers Ollama summary and returns summary + recent messages",
          "type": "integration",
          "file": "backend/tests/test_context_builder.py"
        },
        {
          "id": "TT-408-03",
          "description": "Generated summary checkpoint is stored as an artifact",
          "type": "unit",
          "file": "backend/tests/test_context_builder.py"
        }
      ]
    },
    {
      "id": "T-501",
      "title": "Phase/gate state machine with full lifecycle",
      "description": "Extend the existing StateMachine (state_machine.py) to implement the phase-gate lifecycle: debate -> task_planning -> execution -> review -> merge -> done. Add GateStatus transitions (open, pending_approval, approved, rejected) and enforce that phase transitions require customer gate approval. Refactor existing ConversationState enum and Phase enum to align with the DES-06 phase list. Acceptance criteria: (1) phases follow correct order, (2) gate_status transitions are enforced, (3) phase never auto-advances without approved gate, (4) rejected gate keeps conversation in current phase.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R040",
        "OR-R041",
        "OR-R042"
      ],
      "dependencies": [
        "T-101",
        "T-102"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/state_machine.py",
          "backend/src/agent_orchestrator/orchestrator/models.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-501-01",
          "description": "Valid phase transitions succeed (debate -> task_planning -> execution -> etc.)",
          "type": "unit",
          "file": "backend/tests/test_phase_gate.py"
        },
        {
          "id": "TT-501-02",
          "description": "Phase transition without approved gate raises error",
          "type": "unit",
          "file": "backend/tests/test_phase_gate.py"
        },
        {
          "id": "TT-501-03",
          "description": "Rejected gate keeps conversation in current phase",
          "type": "unit",
          "file": "backend/tests/test_phase_gate.py"
        },
        {
          "id": "TT-501-04",
          "description": "Invalid phase transitions (e.g., debate -> merge) raise InvalidTransition",
          "type": "unit",
          "file": "backend/tests/test_phase_gate.py"
        }
      ]
    },
    {
      "id": "T-502",
      "title": "Phase rollback support",
      "description": "Allow the customer to move a conversation back to a previous phase (e.g., from execution back to debate). Reset gate_status to open on rollback. Emit a system_notice documenting the rollback. Acceptance criteria: (1) rollback transitions to earlier phases are valid, (2) gate_status resets to open on rollback, (3) system_notice is emitted for audit trail.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R043"
      ],
      "dependencies": [
        "T-501"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/state_machine.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "S",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-502-01",
          "description": "Rollback from execution to debate succeeds and resets gate to open",
          "type": "unit",
          "file": "backend/tests/test_phase_gate.py"
        },
        {
          "id": "TT-502-02",
          "description": "Rollback emits system_notice event with rollback details",
          "type": "unit",
          "file": "backend/tests/test_phase_gate.py"
        },
        {
          "id": "TT-502-03",
          "description": "Cannot rollback from done or completed phases",
          "type": "unit",
          "file": "backend/tests/test_phase_gate.py"
        }
      ]
    },
    {
      "id": "T-503",
      "title": "Task planning phase parser",
      "description": "Implement parsing of agent-generated structured task lists during the task_planning phase. Parse the JSON task list format (title, description, scope, dependencies, complexity) from agent responses and create Task records. Validate task structure, detect parallelizable tasks (no dependencies), and present for customer approval. Acceptance criteria: (1) structured task list JSON is parsed from agent response, (2) Task records are created with correct fields, (3) parallelizable tasks (no deps) are identified, (4) invalid task format returns clear error.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R050"
      ],
      "dependencies": [
        "T-501"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/task_planner.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-503-01",
          "description": "Valid structured task list JSON is parsed into Task records",
          "type": "unit",
          "file": "backend/tests/test_task_planner.py"
        },
        {
          "id": "TT-503-02",
          "description": "Tasks with no dependencies are identified as parallelizable",
          "type": "unit",
          "file": "backend/tests/test_task_planner.py"
        },
        {
          "id": "TT-503-03",
          "description": "Invalid task JSON format returns descriptive error",
          "type": "unit",
          "file": "backend/tests/test_task_planner.py"
        }
      ]
    },
    {
      "id": "T-504",
      "title": "Task assignment engine",
      "description": "Implement task assignment logic: query unassigned tasks where all dependencies are done, ordered by priority. Match idle Developer agents to highest-priority tasks. Set task.owner_agent_id and task.status='design', agent.status='running'. One task per agent at a time. Format assignment context for Ollama Team Lead evaluation. Acceptance criteria: (1) only tasks with all dependencies done are assignable, (2) idle agents get highest-priority available task, (3) one task per agent enforced, (4) assignment updates task and agent status correctly.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R050",
        "OR-R051",
        "OR-R052"
      ],
      "dependencies": [
        "T-503",
        "T-601"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/task_assigner.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-504-01",
          "description": "Only tasks with all dependencies done are returned as assignable",
          "type": "unit",
          "file": "backend/tests/test_task_assigner.py"
        },
        {
          "id": "TT-504-02",
          "description": "Idle agent gets highest-priority available task assigned",
          "type": "unit",
          "file": "backend/tests/test_task_assigner.py"
        },
        {
          "id": "TT-504-03",
          "description": "Agent already working on a task does not get a second assignment",
          "type": "unit",
          "file": "backend/tests/test_task_assigner.py"
        },
        {
          "id": "TT-504-04",
          "description": "Assignment updates task owner_agent_id, task status, and agent status",
          "type": "unit",
          "file": "backend/tests/test_task_assigner.py"
        }
      ]
    },
    {
      "id": "T-505",
      "title": "Batch execution with steering integration",
      "description": "Enhance the existing BatchRunner to integrate with SteeringManager and debate context. The batch runner should: (1) include pending steering notes in prompts, (2) use the context builder to create proper agent context payloads, (3) track scheduler_run records with status and timestamps, (4) support continue/stop/steer controls. Acceptance criteria: (1) steering notes are injected into agent prompts, (2) context payload is properly built per turn, (3) scheduler_run records status transitions, (4) continue resumes from paused state.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R060",
        "OR-R061",
        "OR-R062"
      ],
      "dependencies": [
        "T-401",
        "T-407"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/batch_runner.py",
          "backend/src/agent_orchestrator/orchestrator/steering.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-505-01",
          "description": "Steering notes appear in agent prompt prefix when pending",
          "type": "unit",
          "file": "backend/tests/test_batch_runner.py"
        },
        {
          "id": "TT-505-02",
          "description": "Batch pauses after batch_size turns and records scheduler_run as completed",
          "type": "unit",
          "file": "backend/tests/test_batch_runner.py"
        },
        {
          "id": "TT-505-03",
          "description": "Continue from paused state resumes with a new batch",
          "type": "unit",
          "file": "backend/tests/test_batch_runner.py"
        },
        {
          "id": "TT-505-04",
          "description": "Directed steer message (@AgentName) targets specific agent",
          "type": "unit",
          "file": "backend/tests/test_batch_runner.py"
        }
      ]
    },
    {
      "id": "T-506",
      "title": "Work order enforcement (task status transitions)",
      "description": "Implement the task work order state machine: todo -> design -> tdd -> implementing -> testing -> pr_raised, with additional states for in_review, fixing_comments, merging, done, blocked. Enforce valid transitions server-side, reject invalid transitions with 409 Conflict. Support configurable work orders per conversation (e.g., skip TDD for docs tasks). Acceptance criteria: (1) valid transitions succeed, (2) invalid transitions raise error, (3) testing -> implementing allowed on test failure, (4) work order is configurable per conversation.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R070",
        "OR-R071"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/work_order.py",
          "backend/src/agent_orchestrator/orchestrator/models.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-506-01",
          "description": "Valid work order transitions succeed (design -> tdd -> implementing -> etc.)",
          "type": "unit",
          "file": "backend/tests/test_work_order.py"
        },
        {
          "id": "TT-506-02",
          "description": "Invalid transition (e.g., design -> implementing skipping tdd) raises error",
          "type": "unit",
          "file": "backend/tests/test_work_order.py"
        },
        {
          "id": "TT-506-03",
          "description": "testing -> implementing is allowed (test failure rollback)",
          "type": "unit",
          "file": "backend/tests/test_work_order.py"
        },
        {
          "id": "TT-506-04",
          "description": "Configurable work order can skip TDD step for docs tasks",
          "type": "unit",
          "file": "backend/tests/test_work_order.py"
        }
      ]
    },
    {
      "id": "T-507",
      "title": "Agent priority loop evaluator",
      "description": "Implement the priority loop that determines an agent's next action after raising a PR: (1) fix own PR comments, (2) merge own approved PR, (3) review others' PRs, (4) pick next task, (5) idle. The evaluation is performed by Ollama Team Lead. Format the evaluation context (agent's PRs, review assignments, available tasks) for Ollama consumption. Acceptance criteria: (1) priority order is correctly enforced, (2) agent with comments on own PR gets 'fix_comments' action, (3) agent with approved PR gets 'merge' action, (4) idle agent with no work gets 'idle' action.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R080",
        "OR-R081"
      ],
      "dependencies": [
        "T-504",
        "T-506",
        "T-601"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/priority_loop.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-507-01",
          "description": "Agent with comments on own PR gets fix_comments as highest priority action",
          "type": "unit",
          "file": "backend/tests/test_priority_loop.py"
        },
        {
          "id": "TT-507-02",
          "description": "Agent with approved PR and no comments gets merge action",
          "type": "unit",
          "file": "backend/tests/test_priority_loop.py"
        },
        {
          "id": "TT-507-03",
          "description": "Agent assigned as reviewer gets review action when no own PR work needed",
          "type": "unit",
          "file": "backend/tests/test_priority_loop.py"
        },
        {
          "id": "TT-507-04",
          "description": "Agent with no work returns idle action",
          "type": "unit",
          "file": "backend/tests/test_priority_loop.py"
        }
      ]
    },
    {
      "id": "T-508",
      "title": "Resource monitor and concurrency limiter",
      "description": "Implement resource monitoring: capture CPU load, RAM usage, and GPU status periodically (every 60s) and store as resource_snapshot records. Enforce a configurable concurrency limit (max simultaneous agent processes). Integrate with the existing CapacityThrottle to use real system metrics. Acceptance criteria: (1) resource snapshots are captured at configured intervals, (2) concurrency limit blocks new agent starts when at max, (3) queued tasks advance when a slot frees up, (4) dashboard-ready resource data is available via API.",
      "design_refs": [
        "DES-06"
      ],
      "requirements": [
        "OR-R090",
        "OR-R091"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/resource_monitor.py",
          "backend/src/agent_orchestrator/orchestrator/throttle.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-execution",
      "tests": [
        {
          "id": "TT-508-01",
          "description": "Resource snapshot captures CPU load and RAM usage from system",
          "type": "unit",
          "file": "backend/tests/test_resource_monitor.py"
        },
        {
          "id": "TT-508-02",
          "description": "Concurrency limit blocks new agent processes when at max capacity",
          "type": "unit",
          "file": "backend/tests/test_resource_monitor.py"
        },
        {
          "id": "TT-508-03",
          "description": "Queued task starts when active agent slot is freed",
          "type": "unit",
          "file": "backend/tests/test_resource_monitor.py"
        }
      ]
    },
    {
      "id": "T-601",
      "title": "BaseAdapter streaming interface refactor",
      "description": "Refactor the existing BaseAdapter (base.py) to support streaming via AsyncIterator[AdapterEvent]. Add the AdapterEvent dataclass with typed events (thinking, text, tool_call, tool_result, file_edit, shell_command, error, done). Add stop() method for graceful cancellation. Keep backward compatibility with the existing AdapterResult for non-streaming use cases. Acceptance criteria: (1) AdapterEvent dataclass with all event types defined, (2) send_prompt returns AsyncIterator[AdapterEvent], (3) resume_session returns AsyncIterator[AdapterEvent], (4) stop() method added to BaseAdapter, (5) existing AdapterResult is preserved for non-streaming callers.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R001",
        "IN-R002",
        "IN-R003"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/base.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-601-01",
          "description": "AdapterEvent has all required type variants (thinking, text, tool_call, etc.)",
          "type": "unit",
          "file": "backend/tests/test_adapter_base.py"
        },
        {
          "id": "TT-601-02",
          "description": "send_prompt returns AsyncIterator[AdapterEvent] that can be consumed",
          "type": "unit",
          "file": "backend/tests/test_adapter_base.py"
        },
        {
          "id": "TT-601-03",
          "description": "stop() cancels an in-progress operation and yields a done event",
          "type": "unit",
          "file": "backend/tests/test_adapter_base.py"
        }
      ]
    },
    {
      "id": "T-602",
      "title": "Claude adapter streaming JSON output",
      "description": "Refactor the existing ClaudeAdapter to use --output-format stream-json and parse streaming JSON lines into AdapterEvent stream. Map Claude CLI event types (thinking, text, tool_use, tool_result) to AdapterEvent types. Support configurable model, max_tokens, and permission profile (--dangerously-skip-permissions). Acceptance criteria: (1) CLI invoked with --output-format stream-json, (2) JSON lines parsed into typed AdapterEvents as they arrive, (3) model/max_tokens/permission_profile configurable per instance, (4) session resume via --session-id works.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R010",
        "IN-R011",
        "IN-R012"
      ],
      "dependencies": [
        "T-601"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/claude_adapter.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-602-01",
          "description": "Claude CLI is invoked with --output-format stream-json flag",
          "type": "unit",
          "file": "backend/tests/test_claude_adapter.py"
        },
        {
          "id": "TT-602-02",
          "description": "Streaming JSON lines are parsed into correct AdapterEvent types",
          "type": "unit",
          "file": "backend/tests/test_claude_adapter.py"
        },
        {
          "id": "TT-602-03",
          "description": "Model, max_tokens, and permission_profile are configurable per instance",
          "type": "unit",
          "file": "backend/tests/test_claude_adapter.py"
        },
        {
          "id": "TT-602-04",
          "description": "Session resume uses --session-id flag and returns streaming events",
          "type": "unit",
          "file": "backend/tests/test_claude_adapter.py"
        }
      ]
    },
    {
      "id": "T-603",
      "title": "Codex adapter streaming and normalization",
      "description": "Refactor the existing CodexAdapter to support streaming output and normalize Codex CLI events into the standard AdapterEvent stream. Invoke with --approval-mode full-auto and --quiet. Parse Codex-specific output format and map to standard event types. Acceptance criteria: (1) CLI invoked with --approval-mode full-auto, (2) output normalized to AdapterEvent stream, (3) error handling for non-zero exit codes, (4) timeout handling with graceful process cleanup.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R020",
        "IN-R021"
      ],
      "dependencies": [
        "T-601"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/codex_adapter.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-603-01",
          "description": "Codex CLI is invoked with --approval-mode full-auto flag",
          "type": "unit",
          "file": "backend/tests/test_codex_adapter.py"
        },
        {
          "id": "TT-603-02",
          "description": "Codex output is normalized into standard AdapterEvent stream",
          "type": "unit",
          "file": "backend/tests/test_codex_adapter.py"
        },
        {
          "id": "TT-603-03",
          "description": "Non-zero exit code yields error AdapterEvent",
          "type": "unit",
          "file": "backend/tests/test_codex_adapter.py"
        }
      ]
    },
    {
      "id": "T-604",
      "title": "Ollama adapter HTTP API streaming",
      "description": "Refactor the existing Ollama adapter from CLI-based (ollama run) to HTTP API-based (localhost:11434/api/generate). Implement as a class extending BaseAdapter. Support streaming responses, model selection, and availability checking via /api/tags. Enforce role restriction: Ollama is for Team Lead coordination only, not code generation. Acceptance criteria: (1) communicates via HTTP API not CLI, (2) streaming response parsed into AdapterEvent stream, (3) is_available() checks /api/tags, (4) model is configurable per agent.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R030",
        "IN-R031",
        "IN-R032"
      ],
      "dependencies": [
        "T-601"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/ollama_adapter.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-604-01",
          "description": "Ollama adapter uses HTTP API (POST /api/generate) not CLI subprocess",
          "type": "unit",
          "file": "backend/tests/test_ollama_adapter.py"
        },
        {
          "id": "TT-604-02",
          "description": "Streaming HTTP response is parsed into AdapterEvent stream",
          "type": "unit",
          "file": "backend/tests/test_ollama_adapter.py"
        },
        {
          "id": "TT-604-03",
          "description": "is_available() checks /api/tags endpoint and returns bool",
          "type": "unit",
          "file": "backend/tests/test_ollama_adapter.py"
        },
        {
          "id": "TT-604-04",
          "description": "Model is configurable and passed correctly in API request",
          "type": "unit",
          "file": "backend/tests/test_ollama_adapter.py"
        }
      ]
    },
    {
      "id": "T-605",
      "title": "Adapter registry and factory",
      "description": "Implement an adapter registry that maps Provider enum values to adapter classes. Provide a factory function that creates the correct adapter instance based on agent configuration (provider, model, permissions). Support runtime registration of new adapter types for extensibility. Acceptance criteria: (1) get_adapter(provider) returns correct adapter class, (2) factory creates configured instances from agent records, (3) new adapters can be registered at runtime, (4) unknown provider raises clear error.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R040"
      ],
      "dependencies": [
        "T-601",
        "T-602",
        "T-603",
        "T-604"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/__init__.py",
          "backend/src/agent_orchestrator/adapters/registry.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "S",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-605-01",
          "description": "Registry returns correct adapter for each known provider (claude, codex, ollama)",
          "type": "unit",
          "file": "backend/tests/test_adapter_registry.py"
        },
        {
          "id": "TT-605-02",
          "description": "Factory creates configured adapter instance from agent configuration",
          "type": "unit",
          "file": "backend/tests/test_adapter_registry.py"
        },
        {
          "id": "TT-605-03",
          "description": "Unknown provider raises ValueError with descriptive message",
          "type": "unit",
          "file": "backend/tests/test_adapter_registry.py"
        }
      ]
    },
    {
      "id": "T-606",
      "title": "Git worktree manager",
      "description": "Implement a WorktreeManager that creates, lists, and cleans up git worktrees for agent tasks. Path convention: {worktree_base}/{task-slug}/. Branch convention: {provider}/{task-slug}. Configurable worktree base directory (default: ../agent-orchestrator-worktrees/). Lifecycle: create on task assignment, cleanup on merge completion. Acceptance criteria: (1) create_worktree() creates worktree + branch, (2) path follows {base}/{task-slug} convention, (3) branch follows {provider}/{task-slug} convention, (4) cleanup removes worktree and deletes branch.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R090",
        "IN-R091",
        "IN-R092"
      ],
      "dependencies": [
        "T-101"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/worktree.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-606-01",
          "description": "create_worktree produces correct path and branch name from task slug and provider",
          "type": "unit",
          "file": "backend/tests/test_worktree.py"
        },
        {
          "id": "TT-606-02",
          "description": "cleanup_worktree removes worktree directory and deletes branch",
          "type": "unit",
          "file": "backend/tests/test_worktree.py"
        },
        {
          "id": "TT-606-03",
          "description": "Worktree base directory is configurable and defaults to ../agent-orchestrator-worktrees/",
          "type": "unit",
          "file": "backend/tests/test_worktree.py"
        }
      ]
    },
    {
      "id": "T-607",
      "title": "PR detection and metadata capture",
      "description": "Detect when an agent creates a PR (by monitoring git state or parsing agent output for 'gh pr create' commands). Capture PR metadata (number, URL, branch, title) and store with the task record. Acceptance criteria: (1) PR creation detected from agent output stream, (2) PR metadata (number, URL, branch) extracted and stored, (3) task record updated with PR reference, (4) PR detection works for both gh CLI output and git push output.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R060"
      ],
      "dependencies": [
        "T-601",
        "T-606"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/github.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-607-01",
          "description": "PR creation detected from agent output containing 'gh pr create' results",
          "type": "unit",
          "file": "backend/tests/test_github_integration.py"
        },
        {
          "id": "TT-607-02",
          "description": "PR metadata (number, URL, branch, title) correctly extracted",
          "type": "unit",
          "file": "backend/tests/test_github_integration.py"
        },
        {
          "id": "TT-607-03",
          "description": "Task record updated with PR reference after detection",
          "type": "unit",
          "file": "backend/tests/test_github_integration.py"
        }
      ]
    },
    {
      "id": "T-608",
      "title": "GitHub operations helper (gh CLI wrapper)",
      "description": "Implement a GitHubOps helper that wraps the gh CLI for PR operations: list PRs, read review comments, check CI status, post review comments. All operations are performed by the system process or Ollama, not paid agents. Acceptance criteria: (1) list_prs() returns PR metadata, (2) get_review_comments() returns comments for a PR, (3) check_ci_status() returns pass/fail/pending, (4) post_review() posts a review comment.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R061",
        "IN-R071"
      ],
      "dependencies": [
        "T-607"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/github.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-608-01",
          "description": "list_prs() invokes gh pr list and returns structured PR metadata",
          "type": "unit",
          "file": "backend/tests/test_github_integration.py"
        },
        {
          "id": "TT-608-02",
          "description": "get_review_comments() returns parsed review comments for a PR",
          "type": "unit",
          "file": "backend/tests/test_github_integration.py"
        },
        {
          "id": "TT-608-03",
          "description": "check_ci_status() returns correct status (passed, failed, pending)",
          "type": "unit",
          "file": "backend/tests/test_github_integration.py"
        },
        {
          "id": "TT-608-04",
          "description": "post_review() invokes gh pr review with correct arguments",
          "type": "unit",
          "file": "backend/tests/test_github_integration.py"
        }
      ]
    },
    {
      "id": "T-609",
      "title": "CI status monitoring",
      "description": "Implement CI status polling for open PRs every 60 seconds. CI failures are surfaced as task events. The owning agent is notified to fix. Poll CI via 'gh pr checks' command. Acceptance criteria: (1) CI status polled at configurable interval (default 60s), (2) CI failure creates task event, (3) owning agent is notified of CI failure, (4) CI pass transitions merge queue status.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R080"
      ],
      "dependencies": [
        "T-608"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/ci_monitor.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-609-01",
          "description": "CI status is polled at the configured interval for open PRs",
          "type": "unit",
          "file": "backend/tests/test_ci_monitor.py"
        },
        {
          "id": "TT-609-02",
          "description": "CI failure creates a task event and notifies the owning agent",
          "type": "unit",
          "file": "backend/tests/test_ci_monitor.py"
        },
        {
          "id": "TT-609-03",
          "description": "CI pass advances merge queue status from testing to merging",
          "type": "unit",
          "file": "backend/tests/test_ci_monitor.py"
        }
      ]
    },
    {
      "id": "T-610",
      "title": "File access boundary enforcement",
      "description": "Ensure agents can only access files within their worktree and the conversation's project_path. The adapter sets working_dir to the worktree path. Capture all file reads/writes in agent activity logs for the activity viewer. Acceptance criteria: (1) adapter working_dir is set to worktree path, (2) attempts to access files outside boundary are blocked, (3) file operations are logged in activity log.",
      "design_refs": [
        "DES-07"
      ],
      "requirements": [
        "IN-R110",
        "IN-R111"
      ],
      "dependencies": [
        "T-606"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/adapters/sandbox.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/adapters/"
        ]
      },
      "complexity": "S",
      "parallel_group": "orch-adapters",
      "tests": [
        {
          "id": "TT-610-01",
          "description": "Adapter working_dir is set to the agent's worktree path",
          "type": "unit",
          "file": "backend/tests/test_sandbox.py"
        },
        {
          "id": "TT-610-02",
          "description": "File operations outside worktree boundary are detected and logged",
          "type": "unit",
          "file": "backend/tests/test_sandbox.py"
        },
        {
          "id": "TT-610-03",
          "description": "Agent file activity (reads/writes) is captured in activity log",
          "type": "unit",
          "file": "backend/tests/test_sandbox.py"
        }
      ]
    },
    {
      "id": "T-701",
      "title": "Merge queue data model and FIFO operations",
      "description": "Extend the existing MergeCoordinator (merge_queue.py) to support the full merge queue lifecycle: queued -> rebasing -> testing -> merging -> merged, with blocked and failed states. Add PR metadata fields (pr_number, pr_url, author_agent_id, reviewer_agent_id, position). Support customer re-prioritization of queue order. Store queue in merge_queue table. Acceptance criteria: (1) full status lifecycle implemented, (2) FIFO ordering enforced, (3) only one PR active (rebasing/testing/merging) at a time, (4) customer can re-order queue, (5) merge_queue table schema matches MG-R060.",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R001",
        "MG-R002",
        "MG-R003",
        "MG-R060"
      ],
      "dependencies": [
        "T-101",
        "T-102"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/merge_queue.py",
          "backend/src/agent_orchestrator/orchestrator/models.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-701-01",
          "description": "Queue enforces FIFO: first-approved PR is first to process",
          "type": "unit",
          "file": "backend/tests/test_merge_queue.py"
        },
        {
          "id": "TT-701-02",
          "description": "Only one PR can be in rebasing/testing/merging at any time",
          "type": "unit",
          "file": "backend/tests/test_merge_queue.py"
        },
        {
          "id": "TT-701-03",
          "description": "Customer re-prioritization changes queue order",
          "type": "unit",
          "file": "backend/tests/test_merge_queue.py"
        },
        {
          "id": "TT-701-04",
          "description": "Full status lifecycle: queued -> rebasing -> testing -> merging -> merged",
          "type": "unit",
          "file": "backend/tests/test_merge_queue.py"
        }
      ]
    },
    {
      "id": "T-702",
      "title": "Merge process flow (rebase, test, merge)",
      "description": "Implement the merge process: when a PR reaches queue front, (1) git fetch origin main + git rebase origin/main, (2) if conflict -> mark blocked + notify author, (3) if clean -> force-push + advance to testing, (4) wait for CI checks, (5) if CI passes -> merge (squash or regular, configurable), (6) if CI fails -> mark fixing_comments + notify author. Acceptance criteria: (1) rebase executed correctly, (2) conflict detected and marked as blocked, (3) CI pass triggers merge, (4) merge strategy (squash/regular) is configurable.",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R010",
        "MG-R011"
      ],
      "dependencies": [
        "T-701",
        "T-606",
        "T-608"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/merge_process.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "XL",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-702-01",
          "description": "Clean rebase advances PR status from rebasing to testing",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        },
        {
          "id": "TT-702-02",
          "description": "Rebase conflict marks PR as blocked and emits notification",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        },
        {
          "id": "TT-702-03",
          "description": "CI pass triggers merge with configured strategy (squash default)",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        },
        {
          "id": "TT-702-04",
          "description": "While one PR is merging, no other PR can enter rebasing/testing/merging",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        }
      ]
    },
    {
      "id": "T-703",
      "title": "Team Lead coordinator loop",
      "description": "Implement the Ollama Team Lead coordinator loop that runs every 30 seconds (configurable) plus triggers on events (PR raised, PR approved, merge completed). The loop checks: (1) is anything currently merging, (2) advance next queued PR, (3) check rebase results, (4) check CI status, (5) assign reviewers for unreviewed PRs. All coordination runs on Ollama (free). Acceptance criteria: (1) loop runs at configured interval, (2) events trigger immediate evaluation, (3) queue advances automatically when active merge completes, (4) error handling for rebase conflicts, CI failures, merge timeouts.",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R020",
        "MG-R021",
        "MG-R022"
      ],
      "dependencies": [
        "T-701",
        "T-702",
        "T-604"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/coordinator.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "XL",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-703-01",
          "description": "Coordinator loop advances next queued PR when no active merge exists",
          "type": "unit",
          "file": "backend/tests/test_coordinator.py"
        },
        {
          "id": "TT-703-02",
          "description": "Event trigger (PR approved) causes immediate queue evaluation",
          "type": "unit",
          "file": "backend/tests/test_coordinator.py"
        },
        {
          "id": "TT-703-03",
          "description": "Rebase conflict marks PR as blocked and notifies author + customer",
          "type": "unit",
          "file": "backend/tests/test_coordinator.py"
        },
        {
          "id": "TT-703-04",
          "description": "Merge timeout (>10 min) alerts customer",
          "type": "unit",
          "file": "backend/tests/test_coordinator.py"
        }
      ]
    },
    {
      "id": "T-704",
      "title": "Review-to-merge flow orchestration",
      "description": "Implement the full review-to-merge flow: (1) agent raises PR (pr_raised), (2) Team Lead assigns reviewer (in_review), (3) reviewer posts comments or approves, (4) if comments: author fixes (fixing_comments) + re-review loop, (5) if approved: PR enters merge queue (merging). Integrate with work order status transitions. Acceptance criteria: (1) PR raised triggers reviewer assignment, (2) review comments trigger fixing_comments status, (3) re-review loop works after fixes, (4) approval enters PR into merge queue.",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R030"
      ],
      "dependencies": [
        "T-701",
        "T-506",
        "T-507"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/review_flow.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-704-01",
          "description": "PR raised triggers automatic reviewer assignment by Team Lead",
          "type": "unit",
          "file": "backend/tests/test_review_flow.py"
        },
        {
          "id": "TT-704-02",
          "description": "Review comments transition task to fixing_comments status",
          "type": "unit",
          "file": "backend/tests/test_review_flow.py"
        },
        {
          "id": "TT-704-03",
          "description": "Approval enters PR into merge queue with correct position",
          "type": "unit",
          "file": "backend/tests/test_review_flow.py"
        },
        {
          "id": "TT-704-04",
          "description": "Re-review after fixes cycles back through review correctly",
          "type": "unit",
          "file": "backend/tests/test_review_flow.py"
        }
      ]
    },
    {
      "id": "T-705",
      "title": "Reviewer assignment logic",
      "description": "Implement the reviewer selection algorithm: (1) must NOT be the PR author, (2) prefer idle agents, (3) if multiple idle, prefer lightest review load, (4) if no reviewer available (single-developer), flag for customer review. The system enforces non-author reviewer as a hard rule. Acceptance criteria: (1) author is never assigned as own reviewer, (2) idle agents are preferred, (3) lightest load breaks ties, (4) single-developer falls back to customer review.",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R031",
        "MG-R032"
      ],
      "dependencies": [
        "T-703"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/reviewer.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-705-01",
          "description": "Author agent is never assigned as reviewer of own PR",
          "type": "unit",
          "file": "backend/tests/test_reviewer.py"
        },
        {
          "id": "TT-705-02",
          "description": "Idle agent with lightest review load is selected as reviewer",
          "type": "unit",
          "file": "backend/tests/test_reviewer.py"
        },
        {
          "id": "TT-705-03",
          "description": "Single-developer conversation flags PR for customer review",
          "type": "unit",
          "file": "backend/tests/test_reviewer.py"
        }
      ]
    },
    {
      "id": "T-706",
      "title": "Conflict resolution workflow",
      "description": "When git rebase produces conflicts: (1) identify conflicting files from rebase output, (2) create a system_notice event with conflicting files and diff context, (3) prompt the author agent to resolve conflicts in worktree and force-push, (4) restart merge process from rebase step after push, (5) escalate to customer after 3 failed attempts (configurable). Acceptance criteria: (1) conflicting files identified from git output, (2) author agent receives conflict resolution prompt, (3) retry restarts from rebase, (4) escalation after max attempts.",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R040",
        "MG-R041"
      ],
      "dependencies": [
        "T-702"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/conflict_resolver.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "L",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-706-01",
          "description": "Conflicting files are correctly identified from git rebase output",
          "type": "unit",
          "file": "backend/tests/test_conflict_resolver.py"
        },
        {
          "id": "TT-706-02",
          "description": "Author agent receives prompt with conflict details and resolution instructions",
          "type": "unit",
          "file": "backend/tests/test_conflict_resolver.py"
        },
        {
          "id": "TT-706-03",
          "description": "After agent push, merge process restarts from rebase step",
          "type": "unit",
          "file": "backend/tests/test_conflict_resolver.py"
        },
        {
          "id": "TT-706-04",
          "description": "Escalation to customer after 3 failed resolution attempts",
          "type": "unit",
          "file": "backend/tests/test_conflict_resolver.py"
        }
      ]
    },
    {
      "id": "T-707",
      "title": "Post-merge broadcast and cleanup",
      "description": "After each successful merge: (1) broadcast main_updated event to all agents in the conversation, (2) advise agents with open branches to rebase, (3) immediately trigger next PR in queue (no polling delay), (4) set merged task status to done, (5) clean up worktree and delete branch. Log merge events as message_event entries for audit trail. Acceptance criteria: (1) main_updated event broadcast to all agents, (2) next PR triggered immediately, (3) task status set to done, (4) worktree and branch cleaned up, (5) merge events logged.",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R050",
        "MG-R051",
        "MG-R012",
        "MG-R061"
      ],
      "dependencies": [
        "T-702",
        "T-606"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/orchestrator/merge_process.py",
          "backend/src/agent_orchestrator/orchestrator/coordinator.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/orchestrator/"
        ]
      },
      "complexity": "M",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-707-01",
          "description": "main_updated event is broadcast to all conversation agents after merge",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        },
        {
          "id": "TT-707-02",
          "description": "Next PR in queue is triggered immediately (no 30s polling delay)",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        },
        {
          "id": "TT-707-03",
          "description": "Merged task status set to done and worktree cleaned up",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        },
        {
          "id": "TT-707-04",
          "description": "Merge events are logged as message_event entries for audit trail",
          "type": "unit",
          "file": "backend/tests/test_merge_process.py"
        }
      ]
    },
    {
      "id": "T-708",
      "title": "Merge queue dashboard data API",
      "description": "Expose merge queue data for the dashboard: PR title, author agent, queue position, current status (waiting/rebasing/merging/merged/failed). Provide API endpoint that returns the full queue state. Acceptance criteria: (1) API returns all queue entries with metadata, (2) queue position is accurate, (3) status reflects current merge pipeline state, (4) response includes timing data (queued_at, merged_at).",
      "design_refs": [
        "DES-08"
      ],
      "requirements": [
        "MG-R004"
      ],
      "dependencies": [
        "T-701"
      ],
      "scope": {
        "files": [
          "backend/src/agent_orchestrator/api/routes/merge.py"
        ],
        "directories": [
          "backend/src/agent_orchestrator/api/routes/"
        ]
      },
      "complexity": "S",
      "parallel_group": "orch-merge",
      "tests": [
        {
          "id": "TT-708-01",
          "description": "API returns all merge queue entries with PR title, author, position, status",
          "type": "integration",
          "file": "backend/tests/test_merge_api.py"
        },
        {
          "id": "TT-708-02",
          "description": "Queue position accurately reflects FIFO order",
          "type": "unit",
          "file": "backend/tests/test_merge_api.py"
        },
        {
          "id": "TT-708-03",
          "description": "Response includes timing data (queued_at, merged_at)",
          "type": "unit",
          "file": "backend/tests/test_merge_api.py"
        }
      ]
    }
  ]
};
