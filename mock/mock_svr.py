from fastapi import FastAPI
from fastapi import Body
import uvicorn
from fastapi.responses import Response
import json

mock = FastAPI()


@mock.get("/.well-known/agent.json")
async def fetchagent():
    print("fetch agent.json")
    with open("agent.json") as file:
        agent = file.read()
    return Response(content=agent, media_type="application/json")

@mock.post("/")
async def input(data = Body()):
    print("recv:",data)
    with open("mock.json") as file:
        content = file.read()
    return Response(content=content, media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(mock, host="0.0.0.0", port=10005)