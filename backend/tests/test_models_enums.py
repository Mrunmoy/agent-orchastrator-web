"""Tests for T-115: TaskStatus enum alignment + new enums.

TDD tests — written before implementation.
"""

from __future__ import annotations

from agent_orchestrator.orchestrator.models import (
    VALID_TRANSITIONS,
    EventType,
    MergeQueueStatus,
    TaskStatus,
)

# ---------------------------------------------------------------------------
# TT-115-01: TaskStatus enum contains all 11 statuses
# ---------------------------------------------------------------------------


class TestTaskStatusExpanded:
    def test_has_all_eleven_statuses(self):
        expected = {
            "todo",
            "design",
            "tdd",
            "implementing",
            "testing",
            "pr_raised",
            "in_review",
            "fixing_comments",
            "merging",
            "done",
            "blocked",
        }
        actual = {member.value for member in TaskStatus}
        assert actual == expected

    def test_string_values(self):
        assert TaskStatus.TODO.value == "todo"
        assert TaskStatus.DESIGN.value == "design"
        assert TaskStatus.TDD.value == "tdd"
        assert TaskStatus.IMPLEMENTING.value == "implementing"
        assert TaskStatus.TESTING.value == "testing"
        assert TaskStatus.PR_RAISED.value == "pr_raised"
        assert TaskStatus.IN_REVIEW.value == "in_review"
        assert TaskStatus.FIXING_COMMENTS.value == "fixing_comments"
        assert TaskStatus.MERGING.value == "merging"
        assert TaskStatus.DONE.value == "done"
        assert TaskStatus.BLOCKED.value == "blocked"

    def test_is_str_subclass(self):
        """TaskStatus values can be used as plain strings."""
        assert isinstance(TaskStatus.TODO, str)
        assert TaskStatus.TODO == "todo"


# ---------------------------------------------------------------------------
# TT-115-02: VALID_TRANSITIONS allows / blocks expected moves
# ---------------------------------------------------------------------------


class TestValidTransitions:
    def test_todo_to_design_allowed(self):
        assert TaskStatus.DESIGN in VALID_TRANSITIONS[TaskStatus.TODO]

    def test_todo_to_implementing_blocked(self):
        assert TaskStatus.IMPLEMENTING not in VALID_TRANSITIONS[TaskStatus.TODO]

    def test_design_to_tdd_allowed(self):
        assert TaskStatus.TDD in VALID_TRANSITIONS[TaskStatus.DESIGN]

    def test_tdd_to_implementing_allowed(self):
        assert TaskStatus.IMPLEMENTING in VALID_TRANSITIONS[TaskStatus.TDD]

    def test_implementing_to_testing_allowed(self):
        assert TaskStatus.TESTING in VALID_TRANSITIONS[TaskStatus.IMPLEMENTING]

    def test_testing_to_pr_raised_allowed(self):
        assert TaskStatus.PR_RAISED in VALID_TRANSITIONS[TaskStatus.TESTING]

    def test_pr_raised_to_in_review_allowed(self):
        assert TaskStatus.IN_REVIEW in VALID_TRANSITIONS[TaskStatus.PR_RAISED]

    def test_in_review_to_fixing_comments_allowed(self):
        assert TaskStatus.FIXING_COMMENTS in VALID_TRANSITIONS[TaskStatus.IN_REVIEW]

    def test_fixing_comments_to_in_review_allowed(self):
        assert TaskStatus.IN_REVIEW in VALID_TRANSITIONS[TaskStatus.FIXING_COMMENTS]

    def test_in_review_to_merging_allowed(self):
        assert TaskStatus.MERGING in VALID_TRANSITIONS[TaskStatus.IN_REVIEW]

    def test_merging_to_done_allowed(self):
        assert TaskStatus.DONE in VALID_TRANSITIONS[TaskStatus.MERGING]

    def test_any_status_can_go_to_blocked(self):
        for status in TaskStatus:
            if status in (TaskStatus.DONE, TaskStatus.BLOCKED):
                continue
            assert (
                TaskStatus.BLOCKED in VALID_TRANSITIONS[status]
            ), f"{status} should be able to transition to BLOCKED"

    def test_done_is_terminal(self):
        assert len(VALID_TRANSITIONS[TaskStatus.DONE]) == 0

    def test_all_statuses_have_transition_entry(self):
        for status in TaskStatus:
            assert status in VALID_TRANSITIONS, f"{status} missing from VALID_TRANSITIONS"


# ---------------------------------------------------------------------------
# TT-115-03: EventType enum contains all 7 event types
# ---------------------------------------------------------------------------


class TestEventTypeEnum:
    def test_has_all_seven_types(self):
        expected = {
            "chat_message",
            "debate_turn",
            "phase_change",
            "gate_approval",
            "steer",
            "task_update",
            "system_notice",
        }
        actual = {member.value for member in EventType}
        assert actual == expected

    def test_string_values(self):
        assert EventType.CHAT_MESSAGE.value == "chat_message"
        assert EventType.DEBATE_TURN.value == "debate_turn"
        assert EventType.PHASE_CHANGE.value == "phase_change"
        assert EventType.GATE_APPROVAL.value == "gate_approval"
        assert EventType.STEER.value == "steer"
        assert EventType.TASK_UPDATE.value == "task_update"
        assert EventType.SYSTEM_NOTICE.value == "system_notice"

    def test_is_str_subclass(self):
        assert isinstance(EventType.CHAT_MESSAGE, str)


# ---------------------------------------------------------------------------
# TT-115-04: MergeQueueStatus enum contains all 7 statuses
# ---------------------------------------------------------------------------


class TestMergeQueueStatusEnum:
    def test_has_all_seven_statuses(self):
        expected = {
            "queued",
            "rebasing",
            "testing",
            "merging",
            "merged",
            "failed",
            "blocked",
        }
        actual = {member.value for member in MergeQueueStatus}
        assert actual == expected

    def test_string_values(self):
        assert MergeQueueStatus.QUEUED.value == "queued"
        assert MergeQueueStatus.REBASING.value == "rebasing"
        assert MergeQueueStatus.TESTING.value == "testing"
        assert MergeQueueStatus.MERGING.value == "merging"
        assert MergeQueueStatus.MERGED.value == "merged"
        assert MergeQueueStatus.FAILED.value == "failed"
        assert MergeQueueStatus.BLOCKED.value == "blocked"

    def test_is_str_subclass(self):
        assert isinstance(MergeQueueStatus.QUEUED, str)
