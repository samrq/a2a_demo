from common.client import A2AClient, A2ACardResolver
from common.types import TaskState, Task
import asyncclick as click
import asyncio
from uuid import uuid4
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.artifacts import InMemoryArtifactService
from google.adk.events.event import Event as ADKEvent
from google.adk.events.event_actions import EventActions as ADKEventActions

from common import types
from host_agent import HostAgent
from google.genai import types

#manage agent context
class AgentManager:
    def __init__(self):
        self._session_service = InMemorySessionService()
        self._artifact_service = InMemoryArtifactService()
        self._memory_service = InMemoryMemoryService()
        self._host_agent = HostAgent([],None)
        self.app_name = "host"
        self.user_id = "user1"

    def init_agent(self):
        self._host_runner = Runner(
        app_name=self.app_name,
        agent=self._host_agent.create_agent(),
        artifact_service=self._artifact_service,
        session_service=self._session_service,
        memory_service=self._memory_service,
    )

    def register_agent(self, url):
        card_resolver = A2ACardResolver(url)
        card = card_resolver.get_agent_card()
        self._host_agent.register_agent_card(card)


runner = AgentManager()
runner.init_agent()

#TODO:注册远程agent
runner.register_agent("http://localhost:10002")

@click.command
async def invoke():
    #input 
    prompt = click.prompt(
        "\nWhat do you want to send to the agent? (:q or quit to exit)"
    )
    
    #session info
    session_id = uuid4().hex
    print("session_id:", session_id)
    session = runner._session_service.create_session(app_name=runner.app_name, user_id=runner.user_id, session_id=session_id)
    content = types.Content(role='user', parts=[types.Part(text=prompt)])
    events = runner._host_runner.run(user_id=runner.user_id, session_id=session_id, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)


if __name__ == "__main__":

    asyncio.run(invoke())