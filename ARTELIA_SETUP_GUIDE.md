# Artelia Learning Platform - Setup Guide

Complete guide for setting up the Vanna AI assistant for querying the Artelia Learning database with natural language.

---

## 📋 Prerequisites

1. **Python 3.8+** installed
2. **PostgreSQL access** to `artelia_learning` database
3. **OpenRouter API key** (get one at https://openrouter.ai)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
# Core dependencies
pip install vanna[postgres,openai]

# Optional: For data visualization
pip install vanna[visualization]

# Or install everything at once
pip install vanna[postgres,openai,visualization]
```

### Step 2: Set Environment Variables

```bash
# Required: OpenRouter API key
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Required: PostgreSQL connection
export ARTELIA_POSTGRES_CONNECTION="postgresql://user:password@host:port/artelia_learning"

# Optional: Choose a different model
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"  # Default

# Optional: Server port
export PORT="8000"  # Default
```

**Create a `.env` file for convenience:**

```bash
# .env
OPENROUTER_API_KEY=your-openrouter-api-key
ARTELIA_POSTGRES_CONNECTION=postgresql://user:password@host:port/artelia_learning
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
PORT=8000
```

### Step 3: Run the Assistant

**Option A: Command-Line Interface**

```bash
python artelia_learning_agent.py
```

**Option B: Web Interface (Recommended)**

```bash
python artelia_web_server.py
```

Then visit: http://localhost:8000

---

## 🎯 Usage Examples

### Command-Line Usage

```python
import asyncio
from artelia_learning_agent import create_artelia_agent, query_artelia

async def main():
    agent = await create_artelia_agent(
        postgres_connection_string="postgresql://...",
        openrouter_api_key="your-key"
    )

    await query_artelia(
        agent=agent,
        user_email="admin@arteliagroup.com",
        question="How many employees completed GoodHabitz courses in 2024?"
    )

asyncio.run(main())
```

### Example Questions

Here are questions you can ask the assistant:

**Employee Metrics:**
- "How many active employees do we have?"
- "Show me employee distribution by country"
- "What's the breakdown of France vs International employees?"

**Learning Engagement:**
- "What percentage of active employees used any learning platform in 2024?"
- "Show me the top 10 most engaged learners by time spent"
- "Compare learning engagement between business units"

**GoodHabitz:**
- "What are the most popular GoodHabitz courses in 2024?"
- "How many active employees completed at least one GoodHabitz module?"
- "Show me monthly GoodHabitz activity trends for 2024"

**GlobalExam (SCORM):**
- "How many employees used GlobalExam self-paced learning in 2025?"
- "What's the virtual classes credit utilization by business unit?"
- "Show me employees with the highest GlobalExam engagement"

**360Learning:**
- "Show me 360Learning course completions by year"
- "What are the most completed courses in 2024?"
- "Which business units have the highest 360Learning completion rates?"

**Cross-Platform Analysis:**
- "Show me total learning hours across all platforms for 2024"
- "Which employees haven't engaged with any learning platform in the last 6 months?"
- "Compare learning activity between France and International locations"

---

## 🔧 Configuration Options

### Choose a Different LLM Model

OpenRouter supports many models. Popular choices:

```bash
# Claude 3.5 Sonnet (recommended for SQL)
export OPENROUTER_MODEL="anthropic/claude-3.5-sonnet"

# GPT-4 Turbo
export OPENROUTER_MODEL="openai/gpt-4-turbo"

# Llama 3.1 70B (cost-effective)
export OPENROUTER_MODEL="meta-llama/llama-3.1-70b-instruct"

# Google Gemini Pro
export OPENROUTER_MODEL="google/gemini-pro"
```

See all models: https://openrouter.ai/models

### Enable/Disable Features

Edit `artelia_learning_agent.py`:

```python
agent = await create_artelia_agent(
    postgres_connection_string="...",
    openrouter_api_key="...",
    enable_memory=True,        # Learn from successful queries
    enable_visualization=True  # Generate charts
)
```

### Pre-load Example Queries (Recommended)

Uncomment this in `artelia_learning_agent.py` main():

```python
# Pre-load example queries into agent memory
agent_memory = LocalAgentMemory(storage_path="./artelia_agent_memory")
await preload_example_queries(agent_memory)
```

This loads 10 example queries from the documentation so the agent can learn from them.

---

## 🏗️ Architecture

### How It Works

```
User Question
    ↓
Agent receives: "How many employees completed GoodHabitz in 2024?"
    ↓
1. Searches agent memory for similar queries
    ↓
2. Refers to system prompt with database documentation
    ↓
3. Generates SQL:
   SELECT COUNT(DISTINCT au.user_id)
   FROM audit_users au
   INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
   WHERE au.deletion_date IS NULL
     AND gm.lessonstatus = 'completed'
     AND gm.completion_year = 2024
    ↓
4. Executes query via PostgresRunner
    ↓
5. Returns results with natural language summary
    ↓
6. Saves successful pattern to memory
```

### Key Components

1. **ArteliaSystemPromptBuilder**: Injects database documentation into LLM context
2. **PostgresRunner**: Executes SQL queries against your database
3. **Agent Memory**: Learns from successful queries over time
4. **OpenRouter LLM**: Generates SQL from natural language (via OpenAI-compatible API)

---

## 🔒 Security Considerations

### Row-Level Security

By default, all users can query all data. To add row-level security:

```python
from vanna.core.user import UserResolver, User, RequestContext

class ArteliaUserResolver(UserResolver):
    """Custom user resolver with role-based access."""

    async def resolve_user(self, request_context: RequestContext) -> User:
        # Extract user from JWT/session
        token = request_context.metadata.get("Authorization", "")
        user_data = await your_auth_system.verify(token)

        # Define group memberships based on roles
        groups = []
        if user_data["role"] == "admin":
            groups = ["view_all"]
        elif user_data["role"] == "hr":
            groups = ["view_hr"]
        elif user_data["role"] == "manager":
            groups = ["view_team"]

        return User(
            id=user_data["user_id"],
            email=user_data["email"],
            group_memberships=groups,
            metadata={
                "role": user_data["role"],
                "bu": user_data.get("business_unit")
            }
        )

# Use custom resolver
agent = Agent(
    llm_service=llm,
    tool_registry=tool_registry,
    user_resolver=ArteliaUserResolver()  # ← Custom resolver
)
```

### SQL Injection Protection

Vanna uses parameterized queries internally. However, the LLM generates SQL text. To add validation:

```python
from vanna.tools import RunSqlTool

class ValidatedRunSqlTool(RunSqlTool):
    """SQL tool with additional validation."""

    async def execute(self, context, args):
        sql = args.sql.upper()

        # Block dangerous operations
        if any(keyword in sql for keyword in ["DROP", "DELETE", "TRUNCATE", "ALTER"]):
            if context.user.id not in ["admin-user-id"]:
                raise PermissionError("Only admins can run modification queries")

        return await super().execute(context, args)
```

---

## 📊 Monitoring & Logging

### Enable Query Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('artelia_queries.log'),
        logging.StreamHandler()
    ]
)
```

### Track Usage

All queries are stored in agent memory. To export:

```python
from vanna.integrations.local import LocalAgentMemory

agent_memory = LocalAgentMemory(storage_path="./artelia_agent_memory")
recent_queries = await agent_memory.get_recent_memories(context, limit=100)

for memory in recent_queries:
    print(f"Question: {memory.question}")
    print(f"SQL: {memory.args['sql']}")
    print(f"Timestamp: {memory.created_at}")
```

---

## 🐛 Troubleshooting

### Issue: "No module named 'psycopg2'"

**Solution:**
```bash
pip install psycopg2-binary
# Or if using vanna extras:
pip install vanna[postgres]
```

### Issue: "Connection refused" to PostgreSQL

**Solution:**
- Check your connection string
- Verify PostgreSQL is running
- Check firewall/network settings
- Test connection: `psql "postgresql://user:password@host:port/artelia_learning"`

### Issue: Agent generates incorrect SQL

**Solution:**
1. Check if similar query exists in documentation
2. Add the correct query to agent memory manually
3. Review system prompt for clarity
4. Consider using a more powerful model (Claude 3.5 Sonnet recommended)

### Issue: "Rate limit exceeded" from OpenRouter

**Solution:**
- Wait a few seconds between queries
- Upgrade your OpenRouter plan
- Use a less expensive model for testing

---

## 🚀 Deployment

### Production Deployment with Docker

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY artelia_learning_agent.py .
COPY artelia_web_server.py .
COPY DB/DATABASE_DOCUMENTATION.md DB/

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "artelia_web_server.py"]
```

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  artelia-assistant:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ARTELIA_POSTGRES_CONNECTION=${ARTELIA_POSTGRES_CONNECTION}
      - OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
    volumes:
      - ./artelia_agent_memory:/app/artelia_agent_memory
      - ./artelia_query_results:/app/artelia_query_results
    restart: unless-stopped
```

**Deploy:**

```bash
docker-compose up -d
```

---

## 📚 Additional Resources

- **OpenRouter Models**: https://openrouter.ai/models
- **Vanna Documentation**: https://docs.vanna.ai
- **PostgreSQL Connection Strings**: https://www.postgresql.org/docs/current/libpq-connect.html

---

## 💡 Tips & Best Practices

1. **Start with example queries**: Pre-load the 10 example queries from documentation
2. **Monitor agent memory**: Regularly review learned queries for accuracy
3. **Use specific questions**: "Show me X for 2024" works better than "Show me X"
4. **Leverage conversation context**: Ask follow-up questions in same conversation
5. **Test queries manually first**: Verify SQL output before relying on it
6. **Keep documentation updated**: Update DATABASE_DOCUMENTATION.md as schema changes
7. **Use appropriate models**: Claude 3.5 Sonnet excels at SQL, Llama 3.1 is cost-effective

---

**Need help?** Contact your Artelia IT team or refer to the Vanna documentation.
