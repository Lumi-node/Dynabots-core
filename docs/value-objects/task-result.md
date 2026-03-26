# TaskResult

The standard outcome format for all task executions. Rich semantics for workflow control.

---

## Protocol Definition

::: dynabots_core.value_objects.task_result.TaskResult

::: dynabots_core.value_objects.task_result.TaskOutcome

---

## Outcomes

Every TaskResult has one of five outcomes:

### SUCCESS

Task completed successfully with data:

```python
result = TaskResult.success(
    task_id="task_001",
    data={"records": 42, "details": "..."}
)

print(result.is_success)        # True
print(result.data)              # {"records": 42, ...}
print(result.should_continue)   # True (downstream tasks run)
```

### FAILURE

Task failed with an error:

```python
result = TaskResult.failure(
    task_id="task_002",
    error="Database connection failed"
)

print(result.is_failure)        # True
print(result.error_message)     # "Database connection failed"
print(result.should_continue)   # False (stop execution)
```

### NO_ACTION_NEEDED

Nothing to do. Skip downstream tasks but don't mark as error:

```python
result = TaskResult.no_action_needed(
    task_id="task_003",
    reason="Data is already up to date"
)

print(result.is_no_action_needed)  # True
print(result.skip_reason)          # "Data is already up to date"
print(result.should_continue)      # False (downstream skip)
```

Perfect for conditional workflows:

```python
# Example: Email notification task
if user_already_notified():
    return TaskResult.no_action_needed(
        task_id="notify",
        reason="User was already notified yesterday"
    )
else:
    await send_email(user)
    return TaskResult.success(task_id="notify", data={"sent": True})
```

### PARTIAL

Partial success. Some work done, some failed:

```python
result = TaskResult.partial(
    task_id="task_004",
    data={"processed": 35, "failed": 5},
    reason="Timeout after 30s, processed 35/40 records"
)

print(result.outcome)           # TaskOutcome.PARTIAL
print(result.data)              # {"processed": 35, "failed": 5}
print(result.should_continue)   # True (has usable data)
```

Good for resilient workflows—downstream tasks work with partial data.

### SKIPPED

Task was skipped intentionally:

```python
result = TaskResult.skipped(
    task_id="task_005",
    reason="Feature flag disabled for this user"
)

print(result.is_skipped)        # True
print(result.should_continue)   # False (don't continue)
```

---

## Creating Results

### Factory Methods

Use the class methods for clarity:

```python
# Success
TaskResult.success(task_id="...", data={...})

# Failure
TaskResult.failure(task_id="...", error="...")

# No action needed
TaskResult.no_action_needed(task_id="...", reason="...")

# Partial
TaskResult.partial(task_id="...", data={...}, reason="...")

# Skipped
TaskResult.skipped(task_id="...", reason="...")
```

### Direct Constructor

Or use the constructor directly:

```python
from dynabots_core import TaskResult, TaskOutcome

result = TaskResult(
    task_id="task_001",
    outcome=TaskOutcome.SUCCESS,
    data={"count": 42},
    should_continue=True,
)
```

---

## Properties

### Core

```python
result = await agent.process_task(task, context)

print(result.task_id)           # Unique task identifier
print(result.outcome)            # TaskOutcome enum
print(result.data)              # Task-specific data
```

### Status Checks

```python
result.is_success              # outcome == SUCCESS
result.is_failure              # outcome == FAILURE
result.is_no_action_needed     # outcome == NO_ACTION_NEEDED
result.is_skipped              # outcome == SKIPPED

result.is_actionable           # False for FAILURE, NO_ACTION_NEEDED, SKIPPED
                               # True for SUCCESS, PARTIAL
```

### Conditional Execution

```python
# In orchestration framework
result = await agent.process_task(task, context)

if result.should_continue:
    # Run next task with result data
    next_result = await next_task(result.data)
else:
    # Stop execution
    print(f"Stopped: {result.skip_reason}")
    return
```

### Audit Fields

```python
result.timestamp               # When result was created
result.duration_ms            # How long task took (milliseconds)
result.error_message          # Error if FAILURE
result.skip_reason            # Reason if NO_ACTION_NEEDED/SKIPPED
result.metadata               # Custom data
```

---

## Metadata

Attach domain-specific data:

```python
result = TaskResult.success(
    task_id="fetch_data",
    data={"records": 42},
    metadata={
        "source": "database",
        "query_time_ms": 150,
        "cache_hit": False,
        "custom_field": "value"
    },
    duration_ms=200
)

print(result.metadata["query_time_ms"])  # 150
```

Use metadata to:
- Track performance metrics
- Store execution details
- Pass custom data to downstream tasks

---

## Serialization

### To Dictionary

```python
result = TaskResult.success(task_id="task_001", data={"count": 42})

data = result.to_dict()
# {
#     "task_id": "task_001",
#     "outcome": "success",
#     "data": {"count": 42},
#     "should_continue": True,
#     "timestamp": "2024-03-26T...",
#     "duration_ms": None,
#     "error_message": None,
#     "skip_reason": None,
#     "is_actionable": True,
#     "is_success": True,
# }
```

### From Dictionary

```python
data = {
    "task_id": "task_001",
    "outcome": "success",
    "data": {"count": 42},
    ...
}

result = TaskResult.from_dict(data)
```

Good for storage and transmission.

---

## Context for Downstream

Extract context needed by next task:

```python
result = await agent.process_task(task, context)

# Get data formatted for downstream
downstream_context = result.get_context_for_downstream()
# {
#     "task_id": "task_001",
#     "outcome": "success",
#     "data": {...},
#     "is_actionable": True,
#     "should_continue": True,
#     ...custom metadata...
# }

# Pass to next task
next_result = await next_agent.process_task(
    next_task,
    downstream_context
)
```

---

## Example: Conditional Workflow

```python
import asyncio
from dynabots_core import TaskResult

async def workflow():
    """Example workflow with conditional execution."""

    # Task 1: Fetch data
    print("Task 1: Fetching data...")
    result1 = TaskResult.success(
        task_id="fetch",
        data={"records": 100}
    )

    if not result1.should_continue:
        print(f"Stopped at fetch: {result1.skip_reason}")
        return

    # Task 2: Validate data
    print("Task 2: Validating...")
    if result1.data["records"] == 0:
        result2 = TaskResult.no_action_needed(
            task_id="validate",
            reason="No records to validate"
        )
    else:
        result2 = TaskResult.success(
            task_id="validate",
            data={"valid": 100}
        )

    if not result2.should_continue:
        print(f"Stopped at validate: {result2.skip_reason}")
        return

    # Task 3: Process data
    print("Task 3: Processing...")
    try:
        # Simulate processing
        processed = result2.data["valid"] * 2
        result3 = TaskResult.success(
            task_id="process",
            data={"processed": processed}
        )
    except Exception as e:
        result3 = TaskResult.failure(
            task_id="process",
            error=str(e)
        )

    if result3.is_success:
        print(f"Success! Processed: {result3.data['processed']}")
    else:
        print(f"Failed: {result3.error_message}")

asyncio.run(workflow())
```

Output:

```
Task 1: Fetching data...
Task 2: Validating...
Task 3: Processing...
Success! Processed: 200
```

---

## Best Practices

1. **Use factory methods**: `TaskResult.success()` is clearer than constructor.
2. **Always set task_id**: Track which task produced each result.
3. **Clear skip reasons**: Help operators understand conditional skips.
4. **Metadata for context**: Use metadata for execution details.
5. **consistent outcomes**: Always return appropriate outcome (don't return success on partial).

---

## See Also

- [Core Concepts: TaskResult](../getting-started/concepts.md#taskresult)
- [Agent Protocol](../protocols/agent.md)
- [Getting Started](../getting-started/quick-start.md)
