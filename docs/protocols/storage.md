# Storage Protocols

Pluggable persistence backends for workflows, audit logs, caching, and reputation tracking.

All storage protocols are **optional**. DynaBots works fine without any storage. Add it when you need persistence or optimization.

---

## Protocol Definition

::: dynabots_core.protocols.storage.ExecutionStore

::: dynabots_core.protocols.storage.AuditStore

::: dynabots_core.protocols.storage.CacheStore

::: dynabots_core.protocols.storage.ReputationStore

---

## ExecutionStore

Stores completed workflow and trial executions.

### In-Memory Implementation

```python
from dynabots_core import ExecutionStore
from typing import Any, Dict, List, Optional

class MemoryExecutionStore:
    """Simple in-memory execution store."""

    def __init__(self):
        self.workflows = {}

    async def save_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """Save a workflow."""
        self.workflows[workflow_data["id"]] = workflow_data
        return True

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a workflow."""
        return self.workflows.get(workflow_id)

    async def list_workflows(
        self,
        limit: int = 50,
        **filters: Any
    ) -> List[Dict[str, Any]]:
        """List workflows with optional filters."""
        workflows = list(self.workflows.values())

        # Apply filters
        if status := filters.get("status"):
            workflows = [w for w in workflows if w.get("status") == status]
        if user_id := filters.get("user_id"):
            workflows = [w for w in workflows if w.get("user_id") == user_id]

        return workflows[:limit]
```

### PostgreSQL Implementation

```python
from dynabots_core import ExecutionStore
from typing import Any, Dict, List, Optional
import json
import asyncpg

class PostgresExecutionStore:
    """Execution store using PostgreSQL."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def save_workflow(self, workflow_data: Dict[str, Any]) -> bool:
        """Save a workflow."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO workflows (id, data, status, user_id, created_at)
                VALUES ($1, $2, $3, $4, now())
                ON CONFLICT (id) DO UPDATE SET data = $2, status = $3
            """, workflow_data["id"], json.dumps(workflow_data),
                workflow_data.get("status"), workflow_data.get("user_id"))
        return True

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a workflow."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT data FROM workflows WHERE id = $1",
                workflow_id
            )
        return json.loads(row["data"]) if row else None

    async def list_workflows(
        self,
        limit: int = 50,
        **filters: Any
    ) -> List[Dict[str, Any]]:
        """List workflows."""
        async with self.pool.acquire() as conn:
            where_clauses = []
            params = [limit]

            if status := filters.get("status"):
                where_clauses.append("status = $" + str(len(params) + 1))
                params.append(status)

            if user_id := filters.get("user_id"):
                where_clauses.append("user_id = $" + str(len(params) + 1))
                params.append(user_id)

            where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
            query = f"SELECT data FROM workflows {where} ORDER BY created_at DESC LIMIT $1"

            rows = await conn.fetch(query, *params)
            return [json.loads(r["data"]) for r in rows]
```

---

## AuditStore

Immutable audit logs for compliance and forensics.

### File-Based Implementation

```python
from dynabots_core import AuditStore
from typing import Any, Dict
from datetime import datetime
import json
import aiofiles

class FileAuditStore:
    """Audit store writing to files."""

    def __init__(self, base_dir: str = "./audit_logs"):
        self.base_dir = base_dir

    async def log_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Log a workflow event."""
        log_data = {
            "event_type": "workflow",
            "workflow_id": workflow_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        filename = f"{self.base_dir}/workflows/{workflow_id}.jsonl"
        async with aiofiles.open(filename, "a") as f:
            await f.write(json.dumps(log_data) + "\n")

        return True

    async def log_task(
        self,
        workflow_id: str,
        task_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Log a task event."""
        log_data = {
            "event_type": "task",
            "workflow_id": workflow_id,
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }

        filename = f"{self.base_dir}/tasks/{workflow_id}/{task_id}.jsonl"
        async with aiofiles.open(filename, "a") as f:
            await f.write(json.dumps(log_data) + "\n")

        return True

    async def log_error(
        self,
        workflow_id: str,
        error_type: str,
        message: str
    ) -> bool:
        """Log an error event."""
        log_data = {
            "event_type": "error",
            "workflow_id": workflow_id,
            "error_type": error_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
        }

        filename = f"{self.base_dir}/errors/{workflow_id}.jsonl"
        async with aiofiles.open(filename, "a") as f:
            await f.write(json.dumps(log_data) + "\n")

        return True
```

### Azure Blob Implementation

```python
from dynabots_core import AuditStore
from typing import Any, Dict
from datetime import datetime
from azure.storage.blob.aio import BlobContainerClient
import json

class BlobAuditStore:
    """Audit store using Azure Blob Storage (immutable)."""

    def __init__(self, container: BlobContainerClient):
        self.container = container

    async def log_workflow(
        self,
        workflow_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Log workflow to blob."""
        blob_name = f"audit/workflows/{workflow_id}/{datetime.utcnow().isoformat()}.json"
        await self.container.upload_blob(
            blob_name,
            json.dumps(data),
            overwrite=False  # Immutable
        )
        return True

    async def log_task(
        self,
        workflow_id: str,
        task_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """Log task to blob."""
        blob_name = f"audit/workflows/{workflow_id}/tasks/{task_id}/{datetime.utcnow().isoformat()}.json"
        await self.container.upload_blob(blob_name, json.dumps(data), overwrite=False)
        return True

    async def log_error(
        self,
        workflow_id: str,
        error_type: str,
        message: str
    ) -> bool:
        """Log error to blob."""
        blob_name = f"audit/errors/{workflow_id}/{datetime.utcnow().isoformat()}.json"
        error_data = {"error_type": error_type, "message": message}
        await self.container.upload_blob(blob_name, json.dumps(error_data), overwrite=False)
        return True
```

---

## CacheStore

Fast ephemeral storage for patterns and reputation.

### Redis Implementation

```python
from dynabots_core import CacheStore
from typing import Any, Dict, Optional
from redis.asyncio import Redis
import json

class RedisCacheStore:
    """Cache store using Redis."""

    def __init__(self, redis: Redis, ttl_seconds: int = 3600):
        self.redis = redis
        self.ttl = ttl_seconds

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value."""
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Dict[str, Any]) -> bool:
        """Set cached value with TTL."""
        await self.redis.setex(
            key,
            self.ttl,
            json.dumps(value)
        )
        return True

    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        await self.redis.delete(key)
        return True
```

### In-Memory Implementation

```python
from dynabots_core import CacheStore
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
import asyncio

class MemoryCacheStore:
    """Simple in-memory cache with expiration."""

    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = ttl_seconds

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value."""
        if key not in self.cache:
            return None

        value, expiry = self.cache[key]
        if datetime.utcnow() > expiry:
            del self.cache[key]
            return None

        return value

    async def set(self, key: str, value: Dict[str, Any]) -> bool:
        """Set cached value."""
        expiry = datetime.utcnow() + timedelta(seconds=self.ttl)
        self.cache[key] = (value, expiry)
        return True

    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        if key in self.cache:
            del self.cache[key]
        return True
```

---

## ReputationStore

Track agent performance over time.

### PostgreSQL Implementation

```python
from dynabots_core import ReputationStore
from typing import Any, Dict, List
import asyncpg

class PostgresReputationStore:
    """Agent reputation tracking."""

    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_reputation(self, agent_name: str, domain: str) -> float:
        """Get agent reputation for domain."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT score FROM reputation
                WHERE agent_name = $1 AND domain = $2
            """, agent_name, domain)

        return row["score"] if row else 0.5  # Default: neutral

    async def update_reputation(
        self,
        agent_name: str,
        domain: str,
        delta: float
    ) -> bool:
        """Update reputation by delta."""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO reputation (agent_name, domain, score)
                VALUES ($1, $2, $3)
                ON CONFLICT (agent_name, domain)
                DO UPDATE SET score = reputation.score + $3
            """, agent_name, domain, delta)
        return True

    async def get_leaderboard(
        self,
        domain: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top agents for domain."""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT agent_name, score, wins, losses
                FROM reputation
                WHERE domain = $1
                ORDER BY score DESC
                LIMIT $2
            """, domain, limit)

        return [dict(row) for row in rows]
```

---

## Storage in Orchestration

Example: Using storage with ORC Arena

```python
from dynabots_orc import Arena

# With storage
arena = Arena(
    agents=[...],
    judge=judge,
    execution_store=postgres_execution_store,  # Save trials
    audit_store=blob_audit_store,              # Immutable logs
    cache_store=redis_cache,                   # Pattern cache
    reputation_store=postgres_reputation,       # Track scores
)

# Without storage (still works)
arena = Arena(agents=[...], judge=judge)
```

---

## Best Practices

1. **ExecutionStore**: Use for analytics and compliance. SQL database recommended.
2. **AuditStore**: Use immutable storage (Azure Blob, S3, append-only DB). Never allow deletes.
3. **CacheStore**: Use in-memory or Redis. Set reasonable TTLs.
4. **ReputationStore**: SQL database for durability. Cache top agents for performance.
5. **Optional**: Start without storage. Add it when you need persistence.

---

## See Also

- [Core Concepts: Storage](../getting-started/concepts.md#storage-protocols)
- [Orchestration: ORC](../ecosystem/orc.md)
