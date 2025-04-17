from common.client import A2AClient, A2ACardResolver
from common.types import TaskState, Task
import asyncclick as click
import asyncio
from uuid import uuid4
from google.adk.agents.llm_agent import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google.adk.models.lite_llm import LiteLlm

APP_NAME = "demo"
USER_ID = "user"
SESSION_ID = uuid4().hex

root_agent = LlmAgent(
        model= LiteLlm(model="ollama_chat/mistral-small3.1"),
        name="agent",
        description=(
            "you are a helpful agent"
        ),
        instruction="""
        """
    )

session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

async def invoke(query, session_id) -> str:
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=session_id, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


@click.command()
async def cli():
    while True:
        prompt = click.prompt(
            "\nWhat do you want to send to the agent? (:q or quit to exit)"
        )
        if prompt == ":q" or prompt == "quit":
            break
        
        await invoke(prompt, SESSION_ID) 

if __name__ == "__main__":
     asyncio.run(cli())
