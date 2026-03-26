# Tool Protocol

Tools are callable actions agents can use. They have a name, description, and JSON-schema parameters.

---

## Protocol Definition

::: dynabots_core.protocols.tool.Tool

---

## Simple Tool

```python
from dynabots_core import Tool
from typing import Any, Dict

class GreetingTool:
    """A simple greeting tool."""

    @property
    def name(self) -> str:
        return "greet"

    @property
    def description(self) -> str:
        return "Greet someone by name"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The person's name"
                }
            },
            "required": ["name"]
        }

    async def execute(self, name: str) -> dict:
        return {"message": f"Hello, {name}!"}
```

---

## Database Search Tool

```python
from dynabots_core import Tool
from typing import Any, Dict

class DatabaseSearchTool:
    """Search database for records."""

    def __init__(self, db_connection):
        self.db = db_connection

    @property
    def name(self) -> str:
        return "search_database"

    @property
    def description(self) -> str:
        return "Search the database for records matching a query"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query (e.g., 'email:alice@example.com')"
                },
                "table": {
                    "type": "string",
                    "enum": ["users", "orders", "products"],
                    "description": "Which table to search"
                },
                "limit": {
                    "type": "integer",
                    "default": 10,
                    "maximum": 100,
                    "description": "Max results to return"
                }
            },
            "required": ["query", "table"]
        }

    async def execute(
        self,
        query: str,
        table: str,
        limit: int = 10
    ) -> dict:
        """Execute the search."""
        try:
            results = await self.db.search(
                table=table,
                query=query,
                limit=limit
            )
            return {
                "status": "success",
                "count": len(results),
                "results": results
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
```

---

## Calculator Tool

```python
from dynabots_core import Tool
from typing import Any, Dict

class CalculatorTool:
    """Evaluate mathematical expressions."""

    @property
    def name(self) -> str:
        return "calculate"

    @property
    def description(self) -> str:
        return "Evaluate a mathematical expression and return the result"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Math expression (e.g., '2 + 2', 'sqrt(16)', 'sin(3.14159)')"
                }
            },
            "required": ["expression"]
        }

    async def execute(self, expression: str) -> dict:
        """Calculate the expression."""
        import math

        try:
            # Create safe namespace for eval
            safe_dict = {
                "sqrt": math.sqrt,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "e": math.e,
                "__builtins__": {},
            }
            result = eval(expression, safe_dict)
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}
```

---

## Email Tool

```python
from dynabots_core import Tool
from typing import Any, Dict

class SendEmailTool:
    """Send an email."""

    def __init__(self, email_client):
        self.client = email_client

    @property
    def name(self) -> str:
        return "send_email"

    @property
    def description(self) -> str:
        return "Send an email to a recipient"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "format": "email",
                    "description": "Recipient email address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body (plain text)"
                },
                "cc": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "CC recipients (optional)"
                }
            },
            "required": ["to", "subject", "body"]
        }

    async def execute(
        self,
        to: str,
        subject: str,
        body: str,
        cc: list = None
    ) -> dict:
        """Send the email."""
        try:
            message_id = await self.client.send(
                to=to,
                subject=subject,
                body=body,
                cc=cc or []
            )
            return {
                "status": "sent",
                "message_id": message_id,
                "to": to
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
```

---

## Parameters Schema

The `parameters_schema` is JSON Schema format.

### Basic Types

```python
{
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "Person's name"
        },
        "age": {
            "type": "integer",
            "minimum": 0,
            "maximum": 150
        },
        "score": {
            "type": "number",
            "description": "Decimal score"
        },
        "active": {
            "type": "boolean"
        }
    },
    "required": ["name"]
}
```

### Enums

```python
{
    "type": "object",
    "properties": {
        "role": {
            "type": "string",
            "enum": ["admin", "user", "guest"],
            "description": "User role"
        }
    },
    "required": ["role"]
}
```

### Arrays

```python
{
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of tags",
            "minItems": 1,
            "maxItems": 10
        }
    }
}
```

### Defaults

```python
{
    "type": "object",
    "properties": {
        "limit": {
            "type": "integer",
            "default": 10,
            "description": "Max results"
        },
        "sort_by": {
            "type": "string",
            "default": "date",
            "enum": ["date", "name", "score"]
        }
    }
}
```

---

## Using Tools with LLMs

Provide tools to LLMs for function calling:

```python
from dynabots_core import LLMMessage
from dynabots_core.providers import OllamaProvider
from dynabots_core.protocols.llm import ToolDefinition

# Create tools
search_tool = DatabaseSearchTool(db)
calc_tool = CalculatorTool()

# Convert to LLM format
tools = [
    ToolDefinition(
        name=search_tool.name,
        description=search_tool.description,
        parameters=search_tool.parameters_schema
    ),
    ToolDefinition(
        name=calc_tool.name,
        description=calc_tool.description,
        parameters=calc_tool.parameters_schema
    ),
]

# Call LLM with tools
llm = OllamaProvider()
response = await llm.complete(
    messages=[
        LLMMessage(role="user", content="Find users with email like alice and count them")
    ],
    tools=tools,  # Provide available tools
)

# Check if LLM called a tool
if response.tool_calls:
    for call in response.tool_calls:
        tool_name = call["function"]["name"]
        tool_args = call["function"]["arguments"]

        # Execute the tool
        if tool_name == "search_database":
            result = await search_tool.execute(**tool_args)
        elif tool_name == "calculate":
            result = await calc_tool.execute(**tool_args)

        print(f"Tool {tool_name} returned: {result}")
```

---

## Tool Format Conversion

Convert tools to provider-specific formats:

```python
from dynabots_core.protocols.tool import (
    tool_to_openai_format,
    tool_to_anthropic_format
)

my_tool = DatabaseSearchTool(db)

# OpenAI format
openai_format = tool_to_openai_format(my_tool)
# Result: {"type": "function", "function": {...}}

# Anthropic format
anthropic_format = tool_to_anthropic_format(my_tool)
# Result: {"name": "...", "description": "...", "input_schema": {...}}
```

---

## Best Practices

1. **Clear descriptions**: LLMs use descriptions to decide when to call tools.
2. **Specific schemas**: Define exact parameters. Don't be vague.
3. **Error handling**: Tools should handle invalid inputs gracefully.
4. **Async**: Always make execute() async for consistency.
5. **Return format**: Consistent return types (dict) makes parsing easier.

---

## See Also

- [Core Concepts: Tool](../getting-started/concepts.md#tool)
- [LLM Provider Protocol](llm.md)
- [Agent Protocol](agent.md)
