import uuid
import json

from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from redis import asyncio as aredis

redis_client = aredis.from_url("redis://redis:6379", decode_responses=True)

app = FastAPI()

@app.post("/chats")
async def generate_chat_handler(
    user_input: str = Body(..., embed=True),
):
    channel = str(uuid.uuid4())
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel)

    task = {"channel": channel, "user_input": user_input}
    await redis_client.lpush("queue", json.dumps(task))

    async def event_generator():
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            token = message["data"]
            if token == "[DONE]":
                break    
            yield token

        await pubsub.unsubscribe(channel)
        await pubsub.close()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )