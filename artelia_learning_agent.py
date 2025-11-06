"""
Artelia Learning Platform - Vanna AI Implementation
Connects to artelia_learning PostgreSQL database with OpenRouter LLM
"""

import asyncio
import os
from typing import Optional

from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.system_prompt import DefaultSystemPromptBuilder
from vanna.core.user import CookieEmailUserResolver, User, RequestContext
from vanna.integrations.openai import OpenAILlmService
from vanna.integrations.postgres import PostgresRunner
from vanna.integrations.local import LocalAgentMemory
from vanna.tools import RunSqlTool, VisualizeDataTool, LocalFileSystem, create_memory_tools


class ArteliaSystemPromptBuilder(DefaultSystemPromptBuilder):
    """Custom system prompt builder with Artelia database documentation."""

    def __init__(self, documentation_file: str):
        super().__init__(base_prompt=None)

        # Load database documentation
        with open(documentation_file, "r") as f:
            self.db_docs = f.read()

    async def build_system_prompt(self, user: User, tools: list):
        # Get default Vanna prompt
        default_prompt = await super().build_system_prompt(user, tools)

        # Add Artelia-specific database knowledge
        custom_prompt = f"""{default_prompt}

========================================
ARTELIA LEARNING DATABASE DOCUMENTATION
========================================

{self.db_docs}

========================================
CRITICAL QUERY RULES
========================================

1. **ALWAYS FILTER FOR ACTIVE EMPLOYEES:**
   Unless specifically asked for deleted/historical users:
   WHERE deletion_date IS NULL

2. **JOIN PATTERNS (CRITICAL - DIFFERENT TABLES USE DIFFERENT KEYS):**

   GoodHabitz:
   FROM audit_users au
   INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username

   SCORM/GlobalExam:
   FROM audit_users au
   INNER JOIN scorm_attendance_2024 sa ON LOWER(au.email) = LOWER(sa.email)

   360Learning courses:
   FROM audit_users au
   INNER JOIN paths_sessions ps ON au.user_id = ps.user_id

3. **LOCATION GROUPING:**
   CASE WHEN country = 'France' THEN 'France' ELSE 'International' END

4. **TIME CONVERSIONS:**
   - GoodHabitz sessiontime: already in minutes
   - SCORM *_minutes columns: already in minutes
   - To get hours: time_minutes / 60

5. **BUSINESS UNITS:**
   Common BU codes: BRE, EUR, EAMO, IND, VT, MI, APAC, BMI, BP, NORD, ADS, CAN, AF

6. **YEAR FILTERS:**
   For recent data, always consider both 2024 and 2025 unless user specifies.
   Use: completion_year = 2024 OR completion_year = 2025

========================================
QUERY GENERATION WORKFLOW
========================================

BEFORE writing SQL, think through:
1. Which tables contain the data? (audit_users, paths_sessions, goodhabitz_modules, scorm_*)
2. What join key to use? (user_id, email with LOWER(), etc.)
3. Should I filter deletion_date IS NULL? (YES, unless historical data requested)
4. What's the correct year filter? (2024, 2025, or both?)
5. Are there similar examples in the documentation above?

AFTER executing SQL:
- Summarize key findings
- Highlight interesting trends
- Suggest follow-up questions if relevant
"""
        return custom_prompt


async def create_artelia_agent(
    postgres_connection_string: str,
    openrouter_api_key: str,
    documentation_file: str = "DB/DATABASE_DOCUMENTATION.md",
    model: str = "anthropic/claude-3.5-sonnet",
    enable_memory: bool = True,
    enable_visualization: bool = True
) -> Agent:
    """
    Create a Vanna agent for Artelia Learning Platform.

    Args:
        postgres_connection_string: PostgreSQL connection string
            Example: "postgresql://user:password@host:port/artelia_learning"
        openrouter_api_key: Your OpenRouter API key
        documentation_file: Path to DATABASE_DOCUMENTATION.md
        model: OpenRouter model ID (default: Claude 3.5 Sonnet)
        enable_memory: Enable agent memory for learning from queries
        enable_visualization: Enable data visualization tools

    Returns:
        Configured Vanna Agent
    """

    print("🚀 Initializing Artelia Learning Assistant...")

    # 1. Set up custom system prompt with database documentation
    system_prompt_builder = ArteliaSystemPromptBuilder(documentation_file)
    print("✓ Loaded database documentation")

    # 2. Configure OpenRouter as LLM provider (OpenAI-compatible)
    llm = OpenAILlmService(
        model=model,
        api_key=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1",
        extra_client_kwargs={
            "default_headers": {
                "HTTP-Referer": "https://artelia.com",
                "X-Title": "Artelia Learning Assistant"
            }
        }
    )
    print(f"✓ Configured LLM: {model}")

    # 3. Set up PostgreSQL runner
    postgres_runner = PostgresRunner(connection_string=postgres_connection_string)
    print("✓ Connected to PostgreSQL database")

    # 4. Create file system for storing query results
    file_system = LocalFileSystem(working_directory="./artelia_query_results")

    # 5. Create tool registry and register SQL tool
    tool_registry = ToolRegistry()

    sql_tool = RunSqlTool(
        sql_runner=postgres_runner,
        file_system=file_system,
        custom_tool_description=(
            "Execute SQL queries against the Artelia Learning database. "
            "Available tables: audit_users (employees), paths_sessions (360Learning), "
            "goodhabitz_modules (microlearning), scorm_attendance_* (GlobalExam self-paced), "
            "scorm_live_* (GlobalExam virtual classes)."
        )
    )
    tool_registry.register(sql_tool)
    print("✓ Registered SQL execution tool")

    # 6. Optional: Register visualization tool
    if enable_visualization:
        try:
            viz_tool = VisualizeDataTool(file_system=file_system)
            tool_registry.register(viz_tool)
            print("✓ Registered visualization tool")
        except ImportError:
            print("⚠ Plotly not installed. Install with: pip install vanna[visualization]")

    # 7. Optional: Enable agent memory
    if enable_memory:
        agent_memory = LocalAgentMemory(storage_path="./artelia_agent_memory")
        memory_tools = create_memory_tools(agent_memory)
        for tool in memory_tools:
            tool_registry.register(tool)
        print("✓ Enabled agent memory (learns from successful queries)")

    # 8. Configure user resolver
    user_resolver = CookieEmailUserResolver()

    # 9. Create the agent
    agent = Agent(
        llm_service=llm,
        config=AgentConfig(
            stream_responses=True,
            temperature=1.0,
        ),
        tool_registry=tool_registry,
        system_prompt_builder=system_prompt_builder,
        user_resolver=user_resolver,
    )

    print("✓ Agent initialized successfully\n")
    return agent


async def preload_example_queries(agent_memory: LocalAgentMemory):
    """Pre-load agent memory with example queries from documentation."""

    print("📚 Pre-loading example queries into agent memory...")

    # Create dummy context for training
    user = User(id="system", group_memberships=["admin"])
    request_context = RequestContext(metadata={"source": "training"})

    from vanna.core.tool import ToolContext
    tool_context = ToolContext(
        user=user,
        conversation_id="training",
        request_id="training-001",
        request_context=request_context
    )

    # Example queries from documentation
    examples = [
        {
            "question": "How many active employees completed at least one GoodHabitz module in 2024?",
            "sql": """SELECT COUNT(DISTINCT au.user_id) as active_employees
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
WHERE au.deletion_date IS NULL
  AND gm.lessonstatus = 'completed'
  AND gm.completion_year = 2024;"""
        },
        {
            "question": "Show me the top 10 GoodHabitz users by time spent in 2024",
            "sql": """SELECT
    au.first_name || ' ' || au.last_name as full_name,
    au.bu,
    au.country,
    COUNT(*) as modules_completed,
    ROUND(SUM(COALESCE(gm.sessiontime, 0)) / 60.0, 2) as total_hours
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
WHERE au.deletion_date IS NULL
  AND gm.lessonstatus = 'completed'
  AND gm.completion_year = 2024
GROUP BY au.user_id, au.first_name, au.last_name, au.bu, au.country
ORDER BY total_hours DESC
LIMIT 10;"""
        },
        {
            "question": "Compare France vs International for GoodHabitz usage in 2024",
            "sql": """SELECT
    CASE WHEN au.country = 'France' THEN 'France' ELSE 'International' END as location_group,
    COUNT(DISTINCT au.user_id) as active_employees,
    COUNT(*) as total_modules_completed
FROM audit_users au
INNER JOIN goodhabitz_modules gm ON au.user_id = gm.username
WHERE au.deletion_date IS NULL
  AND gm.lessonstatus = 'completed'
  AND gm.completion_year = 2024
GROUP BY location_group
ORDER BY location_group;"""
        },
        {
            "question": "What are the most popular GoodHabitz courses in 2025?",
            "sql": """SELECT
    course_title_en,
    COUNT(*) as completions,
    COUNT(DISTINCT username) as unique_users
FROM goodhabitz_modules
WHERE lessonstatus = 'completed'
  AND completion_year = 2025
GROUP BY course_title_en
ORDER BY completions DESC
LIMIT 15;"""
        },
        {
            "question": "How many active employees used SCORM (GlobalExam) in 2025?",
            "sql": """SELECT COUNT(DISTINCT au.user_id) as active_employees
FROM audit_users au
INNER JOIN scorm_attendance_2025 sa ON LOWER(au.email) = LOWER(sa.email)
WHERE au.deletion_date IS NULL
  AND sa.num_activities_carried_out > 0;"""
        },
        {
            "question": "Show virtual classes credit utilization by business unit in 2025",
            "sql": """SELECT
    au.bu as business_unit,
    COUNT(DISTINCT au.user_id) as registered_users,
    COUNT(DISTINCT CASE WHEN sl.num_credits_consumed > 0 THEN au.user_id END) as active_users,
    SUM(sl.num_credits_allocated) as credits_allocated,
    SUM(sl.num_credits_consumed) as credits_consumed,
    ROUND(100.0 * SUM(sl.num_credits_consumed) / NULLIF(SUM(sl.num_credits_allocated), 0), 2) as utilization_rate_pct
FROM audit_users au
LEFT JOIN scorm_live_2025 sl ON LOWER(au.email) = LOWER(sl.email)
WHERE au.deletion_date IS NULL
  AND sl.num_credits_allocated > 0
GROUP BY au.bu
ORDER BY utilization_rate_pct DESC;"""
        },
        {
            "question": "Show monthly GoodHabitz activity trend for 2024",
            "sql": """SELECT
    TO_CHAR(logdate, 'YYYY-MM') as month,
    COUNT(*) as completions,
    COUNT(DISTINCT username) as unique_users
FROM goodhabitz_modules
WHERE lessonstatus = 'completed'
  AND completion_year = 2024
GROUP BY month
ORDER BY month;"""
        },
        {
            "question": "Count active employees by country",
            "sql": """SELECT country, COUNT(*) as employee_count
FROM audit_users
WHERE deletion_date IS NULL
GROUP BY country
ORDER BY employee_count DESC;"""
        },
        {
            "question": "Show 360Learning course completions by year",
            "sql": """SELECT completion_year, COUNT(*) as completions
FROM paths_sessions
WHERE completion_date IS NOT NULL
GROUP BY completion_year
ORDER BY completion_year;"""
        },
        {
            "question": "What percentage of active employees used any learning platform in 2024?",
            "sql": """WITH active_emp AS (
    SELECT user_id, email FROM audit_users WHERE deletion_date IS NULL
),
goodhabitz_users AS (
    SELECT DISTINCT username as user_id FROM goodhabitz_modules
    WHERE completion_year = 2024 AND lessonstatus = 'completed'
),
scorm_users AS (
    SELECT DISTINCT ae.user_id
    FROM active_emp ae
    INNER JOIN scorm_attendance_2024 sa ON LOWER(ae.email) = LOWER(sa.email)
    WHERE sa.num_activities_carried_out > 0
),
course_users AS (
    SELECT DISTINCT user_id FROM paths_sessions WHERE completion_year = 2024 AND completion_date IS NOT NULL
),
all_learners AS (
    SELECT user_id FROM goodhabitz_users
    UNION
    SELECT user_id FROM scorm_users
    UNION
    SELECT user_id FROM course_users
)
SELECT
    (SELECT COUNT(*) FROM active_emp) as total_active_employees,
    COUNT(DISTINCT al.user_id) as employees_who_learned,
    ROUND(100.0 * COUNT(DISTINCT al.user_id) / (SELECT COUNT(*) FROM active_emp), 2) as engagement_pct
FROM all_learners al;"""
        }
    ]

    for example in examples:
        await agent_memory.save_tool_usage(
            question=example["question"],
            tool_name="run_sql",
            args={"sql": example["sql"]},
            context=tool_context,
            success=True,
            metadata={"source": "documentation"}
        )

    print(f"✓ Pre-loaded {len(examples)} example queries\n")


async def query_artelia(
    agent: Agent,
    user_email: str,
    question: str,
    conversation_id: Optional[str] = None
):
    """
    Send a natural language question to the Artelia Learning database.

    Args:
        agent: Configured Vanna agent
        user_email: Email of the user making the query
        question: Natural language question about learning data
        conversation_id: Optional conversation ID for maintaining context
    """
    # Create request context with user information
    request_context = RequestContext(
        cookies={"user_email": user_email},
        metadata={"source": "artelia_learning"},
        remote_addr="127.0.0.1",
    )

    print(f"\n{'='*80}")
    print(f"🔍 Question: {question}")
    print(f"{'='*80}\n")

    # Send message and stream results
    async for component in agent.send_message(
        request_context=request_context,
        message=question,
        conversation_id=conversation_id or f"session-{user_email}",
    ):
        # Handle different component types
        if hasattr(component, "simple_component") and component.simple_component:
            if hasattr(component.simple_component, "text"):
                text = component.simple_component.text
                if text and text.strip():
                    print(f"💬 {text}\n")

        elif hasattr(component, "rich_component") and component.rich_component:
            rich = component.rich_component
            if hasattr(rich, "rows") and rich.rows:
                print(f"📊 Data table returned: {len(rich.rows)} rows\n")
            elif hasattr(rich, "content"):
                print(f"📊 {rich.content}\n")

        elif hasattr(component, "content") and component.content:
            print(f"💬 {component.content}\n")

    print(f"{'='*80}\n")


async def main():
    """Example usage of Artelia Learning Assistant."""

    # Configuration from environment variables
    postgres_conn = os.getenv(
        "ARTELIA_POSTGRES_CONNECTION",
        "postgresql://user:password@localhost:5432/artelia_learning"
    )
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    if not openrouter_key:
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("Set it with: export OPENROUTER_API_KEY='your-key-here'")
        return

    # Create agent
    agent = await create_artelia_agent(
        postgres_connection_string=postgres_conn,
        openrouter_api_key=openrouter_key,
        documentation_file="DB/DATABASE_DOCUMENTATION.md",
        model="anthropic/claude-3.5-sonnet",
        enable_memory=True,
        enable_visualization=True
    )

    # Pre-load example queries (optional, recommended for first run)
    # Uncomment to load example queries into agent memory:
    # agent_memory = LocalAgentMemory(storage_path="./artelia_agent_memory")
    # await preload_example_queries(agent_memory)

    # Example queries for Artelia Learning Platform
    sample_questions = [
        "How many active employees do we have?",
        "Show me the top 5 most popular GoodHabitz courses in 2024",
        "Compare France vs International for learning engagement in 2024",
        "What's the GlobalExam credit utilization rate by business unit in 2025?",
        "Show me monthly learning activity trends for 2024",
    ]

    user_email = "admin@arteliagroup.com"

    print("\n" + "="*80)
    print("🎓 ARTELIA LEARNING PLATFORM ASSISTANT")
    print("="*80)
    print("Ask questions about employee learning data across:")
    print("  • 360Learning (courses and paths)")
    print("  • GoodHabitz (microlearning modules)")
    print("  • GlobalExam (language learning)")
    print("="*80 + "\n")

    # Run sample questions
    for question in sample_questions[:3]:  # Try first 3 questions
        await query_artelia(
            agent=agent,
            user_email=user_email,
            question=question,
            conversation_id="demo-session"
        )
        await asyncio.sleep(1)  # Brief pause between questions


if __name__ == "__main__":
    asyncio.run(main())
