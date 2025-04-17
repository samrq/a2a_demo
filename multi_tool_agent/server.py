import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from common.server import A2AServer
from common.types import AgentCard, AgentCapabilities, AgentSkill, MissingAPIKeyError
from task_manager import AgentTaskManager
from agent import MultiToolAgent
import click


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
    try:
        capabilities = AgentCapabilities(streaming=False) 
        skill = AgentSkill(
            id="query_weather",
            name="Agent to answer questions about the time and weather in a city",
            description="help user to query time and weather in a city",
            tags=["weather","time"],
            examples=["What's the weather in London?"],
        )
        agent_card = AgentCard(
            name="Weather Agent",
            description="This agent handles the query for the time and weather in a city",
            url=f"http://{host}:{port}/",
            version="1.0.0",
            defaultInputModes=MultiToolAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=MultiToolAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )
        server = A2AServer(
            agent_card=agent_card,
            task_manager=AgentTaskManager(agent=MultiToolAgent()),
            host=host,
            port=port,
        )
        server.start()
    except Exception as e:
        print(f"n error occurred during server startup: {e}")
        exit(1)
    
if __name__ == "__main__":
    main()
