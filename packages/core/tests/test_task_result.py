"""Tests for TaskResult value object."""

import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from dynabots_core.value_objects.task_result import TaskResult, TaskOutcome


class TestTaskOutcomeEnum:
    """Tests for TaskOutcome enum."""

    def test_outcome_values(self):
        """Test TaskOutcome enum values."""
        assert TaskOutcome.SUCCESS.value == "success"
        assert TaskOutcome.FAILURE.value == "failure"
        assert TaskOutcome.NO_ACTION_NEEDED.value == "no_action_needed"
        assert TaskOutcome.PARTIAL.value == "partial"
        assert TaskOutcome.SKIPPED.value == "skipped"

    def test_outcome_from_value(self):
        """Test creating TaskOutcome from string value."""
        assert TaskOutcome("success") == TaskOutcome.SUCCESS
        assert TaskOutcome("failure") == TaskOutcome.FAILURE


class TestTaskResultFactory:
    """Tests for TaskResult factory methods."""

    def test_success_factory(self):
        """Test TaskResult.success() factory method."""
        result = TaskResult.success(
            task_id="test_task",
            data={"key": "value"},
        )

        assert result.task_id == "test_task"
        assert result.outcome == TaskOutcome.SUCCESS
        assert result.data == {"key": "value"}
        assert result.should_continue is True
        assert result.error_message is None
        assert result.skip_reason is None
        assert result.metadata == {}

    def test_success_with_metadata(self):
        """Test TaskResult.success() with metadata."""
        metadata = {"source": "api", "retry_count": 0}
        result = TaskResult.success(
            task_id="fetch_data",
            data=[1, 2, 3],
            metadata=metadata,
            duration_ms=1500,
        )

        assert result.metadata == metadata
        assert result.duration_ms == 1500

    def test_failure_factory(self):
        """Test TaskResult.failure() factory method."""
        result = TaskResult.failure(
            task_id="test_task",
            error="Connection timeout",
        )

        assert result.task_id == "test_task"
        assert result.outcome == TaskOutcome.FAILURE
        assert result.data is None
        assert result.error_message == "Connection timeout"
        assert result.should_continue is False
        assert result.is_failure is True

    def test_failure_with_metadata(self):
        """Test TaskResult.failure() with metadata."""
        result = TaskResult.failure(
            task_id="send_email",
            error="SMTP error",
            metadata={"retry_attempt": 1},
            duration_ms=500,
        )

        assert result.metadata == {"retry_attempt": 1}
        assert result.duration_ms == 500

    def test_no_action_needed_factory(self):
        """Test TaskResult.no_action_needed() factory method."""
        result = TaskResult.no_action_needed(
            task_id="check_cache",
            reason="Data already cached",
        )

        assert result.task_id == "check_cache"
        assert result.outcome == TaskOutcome.NO_ACTION_NEEDED
        assert result.data is None
        assert result.skip_reason == "Data already cached"
        assert result.should_continue is False
        assert result.is_no_action_needed is True

    def test_no_action_needed_with_metadata(self):
        """Test TaskResult.no_action_needed() with metadata."""
        result = TaskResult.no_action_needed(
            task_id="sync_db",
            reason="Already synchronized",
            metadata={"last_sync": "2024-01-01"},
            duration_ms=100,
        )

        assert result.metadata == {"last_sync": "2024-01-01"}
        assert result.duration_ms == 100

    def test_skipped_factory(self):
        """Test TaskResult.skipped() factory method."""
        result = TaskResult.skipped(
            task_id="optional_step",
            reason="User opted out",
        )

        assert result.task_id == "optional_step"
        assert result.outcome == TaskOutcome.SKIPPED
        assert result.data is None
        assert result.skip_reason == "User opted out"
        assert result.should_continue is False
        assert result.is_skipped is True
        assert result.duration_ms == 0

    def test_skipped_with_metadata(self):
        """Test TaskResult.skipped() with metadata."""
        result = TaskResult.skipped(
            task_id="notification",
            reason="User muted",
            metadata={"muted_until": "2025-03-31"},
        )

        assert result.metadata == {"muted_until": "2025-03-31"}

    def test_partial_factory(self):
        """Test TaskResult.partial() factory method."""
        result = TaskResult.partial(
            task_id="batch_process",
            data={"processed": 50, "failed": 5},
            reason="5 items failed validation",
        )

        assert result.task_id == "batch_process"
        assert result.outcome == TaskOutcome.PARTIAL
        assert result.data == {"processed": 50, "failed": 5}
        assert result.skip_reason == "5 items failed validation"
        assert result.should_continue is True
        assert result.is_actionable is True

    def test_partial_with_metadata(self):
        """Test TaskResult.partial() with metadata."""
        result = TaskResult.partial(
            task_id="upload",
            data={"uploaded": 100},
            reason="Partial upload",
            metadata={"resume_token": "xyz"},
            duration_ms=2000,
        )

        assert result.metadata == {"resume_token": "xyz"}
        assert result.duration_ms == 2000


class TestTaskResultProperties:
    """Tests for TaskResult computed properties."""

    def test_is_success(self):
        """Test is_success property."""
        assert TaskResult.success(task_id="t", data={}).is_success is True
        assert TaskResult.failure(task_id="t", error="e").is_success is False
        assert TaskResult.skipped(task_id="t", reason="r").is_success is False

    def test_is_failure(self):
        """Test is_failure property."""
        assert TaskResult.failure(task_id="t", error="e").is_failure is True
        assert TaskResult.success(task_id="t", data={}).is_failure is False
        assert TaskResult.skipped(task_id="t", reason="r").is_failure is False

    def test_is_skipped(self):
        """Test is_skipped property."""
        assert TaskResult.skipped(task_id="t", reason="r").is_skipped is True
        assert TaskResult.success(task_id="t", data={}).is_skipped is False
        assert TaskResult.failure(task_id="t", error="e").is_skipped is False

    def test_is_no_action_needed(self):
        """Test is_no_action_needed property."""
        result = TaskResult.no_action_needed(task_id="t", reason="no action")
        assert result.is_no_action_needed is True

        assert TaskResult.success(task_id="t", data={}).is_no_action_needed is False

    def test_is_actionable_success(self):
        """Test is_actionable for success results."""
        result = TaskResult.success(task_id="t", data={"value": 123})
        assert result.is_actionable is True

    def test_is_actionable_partial(self):
        """Test is_actionable for partial results."""
        result = TaskResult.partial(
            task_id="t",
            data={"partial": True},
            reason="some failed",
        )
        assert result.is_actionable is True

    def test_is_actionable_failure(self):
        """Test is_actionable for failure results."""
        result = TaskResult.failure(task_id="t", error="failed")
        assert result.is_actionable is False

    def test_is_actionable_no_action_needed(self):
        """Test is_actionable for no_action_needed results."""
        result = TaskResult.no_action_needed(task_id="t", reason="no action")
        assert result.is_actionable is False

    def test_is_actionable_skipped(self):
        """Test is_actionable for skipped results."""
        result = TaskResult.skipped(task_id="t", reason="skipped")
        assert result.is_actionable is False


class TestTaskResultSerialization:
    """Tests for TaskResult serialization/deserialization."""

    def test_to_dict_success(self):
        """Test to_dict() for success result."""
        result = TaskResult.success(
            task_id="test_task",
            data={"count": 42},
            metadata={"source": "api"},
            duration_ms=1000,
        )

        result_dict = result.to_dict()

        assert result_dict["task_id"] == "test_task"
        assert result_dict["outcome"] == "success"
        assert result_dict["data"] == {"count": 42}
        assert result_dict["metadata"] == {"source": "api"}
        assert result_dict["should_continue"] is True
        assert result_dict["duration_ms"] == 1000
        assert result_dict["is_actionable"] is True
        assert result_dict["is_success"] is True
        assert "timestamp" in result_dict
        assert result_dict["error_message"] is None

    def test_to_dict_failure(self):
        """Test to_dict() for failure result."""
        result = TaskResult.failure(
            task_id="failed_task",
            error="Database connection failed",
            duration_ms=500,
        )

        result_dict = result.to_dict()

        assert result_dict["task_id"] == "failed_task"
        assert result_dict["outcome"] == "failure"
        assert result_dict["data"] is None
        assert result_dict["error_message"] == "Database connection failed"
        assert result_dict["should_continue"] is False
        assert result_dict["is_actionable"] is False

    def test_from_dict_success(self):
        """Test from_dict() for success result."""
        original = TaskResult.success(
            task_id="create_record",
            data={"id": "rec_123", "created": True},
            metadata={"user": "alice"},
            duration_ms=2000,
        )

        dict_repr = original.to_dict()
        reconstructed = TaskResult.from_dict(dict_repr)

        assert reconstructed.task_id == original.task_id
        assert reconstructed.outcome == original.outcome
        assert reconstructed.data == original.data
        assert reconstructed.metadata == original.metadata
        assert reconstructed.duration_ms == original.duration_ms
        assert reconstructed.should_continue == original.should_continue

    def test_from_dict_failure(self):
        """Test from_dict() for failure result."""
        original = TaskResult.failure(
            task_id="send_email",
            error="SMTP timeout",
            metadata={"retry_count": 3},
            duration_ms=1000,
        )

        dict_repr = original.to_dict()
        reconstructed = TaskResult.from_dict(dict_repr)

        assert reconstructed.task_id == original.task_id
        assert reconstructed.outcome == original.outcome
        assert reconstructed.error_message == original.error_message
        assert reconstructed.metadata == original.metadata
        assert reconstructed.duration_ms == original.duration_ms

    def test_from_dict_partial(self):
        """Test from_dict() for partial result."""
        original = TaskResult.partial(
            task_id="batch_job",
            data={"succeeded": 100, "failed": 5},
            reason="5 items failed",
            metadata={"batch_id": "b_789"},
        )

        dict_repr = original.to_dict()
        reconstructed = TaskResult.from_dict(dict_repr)

        assert reconstructed.outcome == TaskOutcome.PARTIAL
        assert reconstructed.data == original.data
        assert reconstructed.skip_reason == original.skip_reason

    def test_from_dict_skipped(self):
        """Test from_dict() for skipped result."""
        original = TaskResult.skipped(
            task_id="optional_task",
            reason="User disabled",
            metadata={"feature_flag": "disabled"},
        )

        dict_repr = original.to_dict()
        reconstructed = TaskResult.from_dict(dict_repr)

        assert reconstructed.outcome == TaskOutcome.SKIPPED
        assert reconstructed.skip_reason == original.skip_reason
        assert reconstructed.metadata == original.metadata

    def test_serialization_roundtrip_preserves_properties(self):
        """Test that serialization roundtrip preserves all properties."""
        results = [
            TaskResult.success(task_id="s1", data=[1, 2, 3]),
            TaskResult.failure(task_id="f1", error="error msg"),
            TaskResult.no_action_needed(task_id="n1", reason="reason"),
            TaskResult.skipped(task_id="sk1", reason="skip reason"),
            TaskResult.partial(task_id="p1", data={"ok": True}, reason="partial"),
        ]

        for original in results:
            reconstructed = TaskResult.from_dict(original.to_dict())
            assert reconstructed.is_success == original.is_success
            assert reconstructed.is_failure == original.is_failure
            assert reconstructed.is_skipped == original.is_skipped
            assert reconstructed.is_actionable == original.is_actionable
            assert reconstructed.should_continue == original.should_continue

    def test_to_dict_includes_timestamp(self):
        """Test that to_dict() includes ISO format timestamp."""
        result = TaskResult.success(task_id="t", data={})
        result_dict = result.to_dict()

        # Timestamp should be ISO format string
        timestamp_str = result_dict["timestamp"]
        assert isinstance(timestamp_str, str)
        # Parse to verify it's valid ISO format
        parsed = datetime.fromisoformat(timestamp_str)
        assert parsed.tzinfo is not None  # Should have timezone


class TestTaskResultContextExtraction:
    """Tests for context extraction for downstream tasks."""

    def test_get_context_for_downstream(self):
        """Test get_context_for_downstream() includes essential fields."""
        result = TaskResult.success(
            task_id="fetch_user",
            data={"user_id": 123, "name": "Alice"},
            metadata={"source": "api", "cached": False},
        )

        context = result.get_context_for_downstream()

        assert context["task_id"] == "fetch_user"
        assert context["outcome"] == "success"
        assert context["data"] == {"user_id": 123, "name": "Alice"}
        assert context["is_actionable"] is True
        assert context["should_continue"] is True
        assert context["source"] == "api"
        assert context["cached"] is False

    def test_context_includes_metadata(self):
        """Test that get_context_for_downstream() spreads metadata."""
        metadata = {
            "execution_time": 150,
            "cache_hit": True,
            "api_version": "v2",
        }
        result = TaskResult.success(
            task_id="t",
            data={"value": 1},
            metadata=metadata,
        )

        context = result.get_context_for_downstream()

        # All metadata fields should be in context
        assert context["execution_time"] == 150
        assert context["cache_hit"] is True
        assert context["api_version"] == "v2"

    def test_context_for_failure(self):
        """Test get_context_for_downstream() for failure result."""
        result = TaskResult.failure(
            task_id="fetch_data",
            error="Connection refused",
            metadata={"retry_count": 2},
        )

        context = result.get_context_for_downstream()

        assert context["task_id"] == "fetch_data"
        assert context["outcome"] == "failure"
        assert context["is_actionable"] is False
        assert context["should_continue"] is False
        assert context["retry_count"] == 2


class TestTaskResultImmutability:
    """Tests for TaskResult frozen dataclass properties."""

    def test_cannot_mutate_task_id(self):
        """Test that task_id is immutable."""
        result = TaskResult.success(task_id="task", data={})

        with pytest.raises(AttributeError):
            result.task_id = "new_task"

    def test_cannot_mutate_outcome(self):
        """Test that outcome is immutable."""
        result = TaskResult.success(task_id="task", data={})

        with pytest.raises(AttributeError):
            result.outcome = TaskOutcome.FAILURE

    def test_cannot_mutate_data(self):
        """Test that data is immutable."""
        result = TaskResult.success(task_id="task", data={"count": 10})

        with pytest.raises(AttributeError):
            result.data = {"count": 20}

    def test_cannot_mutate_should_continue(self):
        """Test that should_continue is immutable."""
        result = TaskResult.success(task_id="task", data={})

        with pytest.raises(AttributeError):
            result.should_continue = False

    def test_cannot_mutate_metadata(self):
        """Test that metadata dict itself is immutable (but contents might change)."""
        result = TaskResult.success(
            task_id="task",
            data={},
            metadata={"key": "value"},
        )

        # The metadata reference itself cannot be changed
        with pytest.raises(AttributeError):
            result.metadata = {"new_key": "new_value"}

        # But the dict contents could be mutated (frozen only freezes the dataclass fields)
        # This is normal dataclass behavior - we test the frozen aspect works
        assert result.metadata == {"key": "value"}


class TestTaskResultEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_complex_data_structures(self):
        """Test TaskResult with complex nested data."""
        complex_data = {
            "users": [
                {"id": 1, "name": "Alice", "scores": [10, 20, 30]},
                {"id": 2, "name": "Bob", "scores": [15, 25, 35]},
            ],
            "metadata": {
                "total": 2,
                "filtered": False,
            },
        }

        result = TaskResult.success(task_id="fetch_users", data=complex_data)
        assert result.data == complex_data

        # Roundtrip
        dict_repr = result.to_dict()
        reconstructed = TaskResult.from_dict(dict_repr)
        assert reconstructed.data == complex_data

    def test_none_data_values(self):
        """Test TaskResult with None as data."""
        result = TaskResult.success(task_id="t", data=None)
        assert result.data is None

        dict_repr = result.to_dict()
        reconstructed = TaskResult.from_dict(dict_repr)
        assert reconstructed.data is None

    def test_empty_string_error_message(self):
        """Test failure result with empty error message."""
        result = TaskResult.failure(task_id="t", error="")
        assert result.error_message == ""

    def test_very_large_duration(self):
        """Test with very large duration_ms values."""
        result = TaskResult.success(
            task_id="t",
            data={},
            duration_ms=999999999,
        )
        assert result.duration_ms == 999999999

    def test_zero_duration(self):
        """Test with zero duration."""
        result = TaskResult.success(task_id="t", data={}, duration_ms=0)
        assert result.duration_ms == 0

    def test_default_metadata_is_empty_dict(self):
        """Test that default metadata is empty dict, not None."""
        result = TaskResult.success(task_id="t", data={})
        assert result.metadata == {}
        assert isinstance(result.metadata, dict)

    def test_timestamp_is_utc(self):
        """Test that timestamp is UTC timezone aware."""
        result = TaskResult.success(task_id="t", data={})
        assert result.timestamp.tzinfo is not None
        # Should be UTC or have timezone info
        assert result.timestamp.tzinfo == timezone.utc


class TestTaskResultIntegration:
    """Integration tests combining multiple features."""

    def test_workflow_with_conditional_execution(self):
        """Test using TaskResult properties for workflow control."""
        # Task 1: Fetch data
        task1 = TaskResult.success(
            task_id="fetch_data",
            data={"records": []},
        )
        assert task1.should_continue is True

        # Task 2: Process data - no action needed if empty
        if task1.data.get("records"):
            task2 = TaskResult.success(task_id="process", data={})
        else:
            task2 = TaskResult.no_action_needed(
                task_id="process",
                reason="No records to process",
            )

        assert task2.should_continue is False
        assert not task2.is_actionable

    def test_error_recovery_workflow(self):
        """Test error handling with retries."""
        for attempt in range(3):
            result = TaskResult.failure(
                task_id="api_call",
                error=f"Attempt {attempt + 1} failed",
                metadata={"attempt": attempt + 1},
            )

            if result.is_failure:
                if attempt < 2:
                    continue  # Retry
                else:
                    # Give up after 3 attempts
                    assert result.metadata["attempt"] == 3
                    break

    def test_batch_processing_partial_success(self):
        """Test batch job with partial success."""
        batch_result = TaskResult.partial(
            task_id="batch_import",
            data={
                "total": 100,
                "successful": 95,
                "failed": 5,
                "failed_ids": [1, 5, 23, 45, 78],
            },
            reason="5 items failed validation",
            metadata={"batch_id": "b123", "timestamp": "2024-01-01"},
        )

        assert batch_result.is_actionable  # Can continue with retry
        assert batch_result.should_continue
        assert batch_result.data["successful"] == 95

        context = batch_result.get_context_for_downstream()
        # Data is passed through context
        assert context["data"]["failed_ids"] == [1, 5, 23, 45, 78]
        # Metadata is spread into context
        assert context["batch_id"] == "b123"
