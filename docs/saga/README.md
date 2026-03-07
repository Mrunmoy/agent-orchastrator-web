# The Orchestrator Saga -- Campaign Log

*A chronicle of the Agent Orchestrator party's quest to build a multi-agent command center from nothing but a Nix shell and raw ambition.*

This directory is the campaign journal. Each quest (milestone) records what the party accomplished, what loot they gained (features, tests), what traps they fell into (review findings), and what new regions of the map they unlocked for the next expedition.

## The Party

- **The Dungeon Master** -- coordinates quests, reviews loot, decides what to tackle next
- **Claude Agents** -- a squad of parallel adventurers, each working an isolated worktree dungeon
- **GitHub CI** -- the gatekeeper who won't let anyone into the main keep without passing trials

## Campaign Rules

- **Test-Driven Development** -- write the tests (traps) before the code (treasure). No exceptions.
- **Worktree Isolation** -- up to 5 party members operate in parallel, each in their own dungeon instance. No stepping on each other's loot.
- **PR Review Gates** -- every quest completion goes through the Dungeon Master's review before merging to the main keep.
- **Track Your Kills** -- every quest updates TASKS.md, task-board.md, and tasks.json. (Added after Quest 3 when the party realized nobody was updating the quest log.)

## Quest Index

| Quest | Title | Party Size | Loot (Tests) | PRs |
|-------|-------|-----------|-------------|-----|
| [01](milestone-01-foundations.md) | The Foundation Stones | Solo | ~10 | Pre-PR era |
| [02](milestone-02-core-infrastructure.md) | The Ten-Headed Hydra | Full party | ~214 | Merge queue |
| [03](milestone-03-orchestration-engine.md) | First Raid: The Engine Room | 5 parallel | ~70 | PRs #1-5 |
| [04](milestone-04-execution-runtime.md) | Second Raid: The Batch Forge | 5 parallel | ~56 | PRs #6-10 |
| [05](milestone-05-coordination-layer.md) | Third Raid: The War Room | 5 parallel | ~93 | PRs #11-15 |
| [06](milestone-06-production-readiness.md) | Fourth Raid: Fortifying the Keep | 5 parallel | ~149 | PRs #16-21 |

**Total loot accumulated: 430+ tests across 40+ test files.**

## Related Scrolls

- **Task Board** (`docs/coordination/task-board.md`) -- the real-time quest tracker
- **TASKS.md** -- the master quest log with completion checkboxes
- **ADRs** (`docs/decisions/`) -- the party's architectural rulings
- **Playbooks** (`docs/playbook/`) -- field guides for when things go sideways
