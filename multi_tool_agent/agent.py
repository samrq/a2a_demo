import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import litellm

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    print("in remote agent", city)
    if city.lower() == "new york":
        return {
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (41 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """

    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "success", "report": report}

class MultiToolAgent:

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
    def __init__(self):
        #litellm._turn_on_debug()
        self._agent = self.create_agent()
        self._user_id="userid1"
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def create_agent(self):
        return Agent(
            name="weather_time_agent",
            #model=LiteLlm(model="ollama_chat/mistral-small3.1"),
            model=LiteLlm(
                api_base='http://localhost:11434/v1',
                model='openai/mistral-small3.1'
            ),
            description=(
                "Agent to answer questions about the time and weather in a city."
            ),
            instruction=(
                "You are a helpful agent who can answer user questions about the time and weather in a city."
            ),
            tools=[get_weather, get_current_time],
        )
    
    def invoke(self, query, session_id) -> str:
        session = self._runner.session_service.get_session(
            app_name=self._agent.name, user_id=self._user_id, session_id=session_id
        )
        content = types.Content(
            role="user", parts=[types.Part.from_text(text=query)]
        )
        if session is None:
          session = self._runner.session_service.create_session(
              app_name=self._agent.name,
              user_id=self._user_id,
              state={},
              session_id=session_id,
          )
        events = list(self._runner.run(
            user_id=self._user_id, session_id=session.id, new_message=content
        ))
        if not events or not events[-1].content or not events[-1].content.parts:
          return ""
        return "\n".join([p.text for p in events[-1].content.parts if p.text])

    async def stream(self, query, session_id):
        session = self._runner.session_service.get_session(
        app_name=self._agent.name, user_id=self._user_id, session_id=session_id
        )
        content = types.Content(
            role="user", parts=[types.Part.from_text(text=query)]
        )
        if session is None:
          session = self._runner.session_service.create_session(
              app_name=self._agent.name,
              user_id=self._user_id,
              state={},
              session_id=session_id,
          )
        async for event in self._runner.run_async(
            user_id=self._user_id, session_id=session.id, new_message=content
        ):
          if event.is_final_response():
            response = ""
            if (
                event.content
                and event.content.parts
                and event.content.parts[0].text
            ):
              response = "\n".join([p.text for p in event.content.parts if p.text])
            elif (
                event.content
                and event.content.parts
                and any([True for p in event.content.parts if p.function_response])):
              response = next((p.function_response.model_dump() for p in event.content.parts))
            yield {
                "is_task_complete": True,
                "content": response,
            }
          else:
            yield {
                "is_task_complete": False,
                "updates": "Processing the request...",    
            }    
