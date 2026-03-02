import os
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPServerParams,
)

BASE_DIR = Path(__file__).parent

ASTA_INSTRUCTION = (BASE_DIR / "prompts/asta.md").read_text()
LINEAR_INSTRUCTION = (BASE_DIR / "prompts/linear.md").read_text()

linear_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="LinearAgent",
    description="Specialist for managing Linear issues, tasks, and project tracking. Cannot answer general questions.",
    instruction=LINEAR_INSTRUCTION,
    tools=[
        McpToolset(
            connection_params=StreamableHTTPServerParams(
                url="https://mcp.linear.app/mcp",
                headers={
                    "Authorization": f"Bearer {os.getenv('LINEAR_API_KEY')}",
                },
            ),
            tool_filter=[
                "get_issue",
                "list_issues",
                "update_issue",
                "create_issue",
            ],
        ),
    ],
    output_key="linear_agent",
)

# Notion Specialist: Only manages long-term tracking and data
# notion_agent = Agent(
#     model="gemini-2.5-pro",
#     name="NotionAgent",
#     instruction="Help users get information from Notion",
#     tools=[
#         McpToolset(
#             connection_params=StdioConnectionParams(
#                 server_params=StdioServerParameters(
#                     command="npx",
#                     args=[
#                         "-y",
#                         "@notionhq/notion-mcp-server",
#                     ],
#                     env={
#                         "NOTION_TOKEN": os.getenv("NOTION_TOKEN"),
#                     },
#                 ),
#                 timeout=30,
#             ),
#         )
#     ],
# )
# --- 2. Define the Orchestrator (Root Agent) ---

orchestrator = LlmAgent(
    model="gemini-2.5-flash",  # Use the powerful model for the "Brain"
    name="Orchestrator",
    description="Asta is the user's Personal Assistant (PA) and central orchestrator.",
    instruction=ASTA_INSTRUCTION,
    sub_agents=[
        linear_agent,
    ],  # This enables the "Council of Agents"
    output_key="asta",
)

# --- 3. Export for ADK Discovery ---
root_agent = orchestrator
