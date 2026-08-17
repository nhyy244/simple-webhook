from enum import Enum
from pathlib import Path
from uuid import UUID

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class EventName(Enum):
    ADD = "add"
    SUBSTRACT = "substract"


events = [EventName.ADD, EventName.SUBSTRACT]


class Event(BaseModel):
    name: EventName


class EventResponse(Event):
    id: UUID


class WebhookSubscription(BaseModel):
    url: str
    events: list[Event]


class WebhookPayload(BaseModel):
    event: EventResponse
    description: str


class Pair(BaseModel):
    a: int
    b: int


@app.post("/add", response_model=int)
def add(number_pair: Pair):
    return number_pair.a + number_pair.b


@app.post("/substract", response_model=int)
def substract(number_pair: Pair):
    return number_pair.a - number_pair.b


@app.post("/register-webhook", response_model=WebhookSubscription)
def register_webhook(webhook_subscription: WebhookSubscription):
    bad_events = [
        event for event in webhook_subscription.events if event.name not in events
    ]
    if len(bad_events) > 0:
        raise HTTPException(
            status_code=202,
            detail=f"these events are not supported: {bad_events}. Supported events: {events}",
        )

    urls = Path("webhooks.txt")
    if urls.exists():
        with open(urls, "r") as file:
            for line in file:
                webhook_sub = WebhookSubscription.model_validate_json(line)
                if webhook_subscription.url == webhook_sub.url:
                    raise HTTPException(
                        status_code=202,
                        detail=f"{webhook_subscription.url} already receiving events",
                    )

    with open(urls, "a") as file:  # creates webhooks.txt if it doesn't exist
        file.write(f"{webhook_subscription.model_dump_json()}\n")

    return WebhookSubscription(
        url=webhook_subscription.url, events=webhook_subscription.events
    )


if __name__ == "__main__":
    uvicorn.run("publisher:app", host="localhost", port=8000, reload=True)
