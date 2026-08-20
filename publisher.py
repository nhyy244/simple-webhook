import uuid
from enum import Enum
from pathlib import Path
from uuid import UUID

import requests
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


class WebhookSubscriptionResponse(BaseModel):
    url: str
    events: list[Event]
    description: str


class WebhookSubscriptionRequest(BaseModel):
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
    webhook_subscriptions_file = Path("webhook_subscriptions.txt")
    if webhook_subscriptions_file.exists():
        with open(webhook_subscriptions_file, "r") as file:
            lines = file.readlines()

        for line in lines:
            if not line.strip():
                continue
            webhook_sub = WebhookSubscriptionRequest.model_validate_json(line)
            for e in webhook_sub.events:
                if e.name.value == EventName.ADD.value:
                    sum = number_pair.a + number_pair.b
                    webhook_response = WebhookPayload(
                        event=EventResponse(name=EventName.ADD, id=uuid.uuid1()),
                        description=f"{EventName.ADD} event received. sum of {number_pair.a} and {number_pair.b} is {sum}",
                    )
                    requests.post(
                        webhook_sub.url, json=webhook_response.model_dump(mode="json")
                    )

    return sum


@app.post("/substract", response_model=int)
def substract(number_pair: Pair):
    webhook_subscriptions_file = Path("webhook_subscriptions.txt")
    if webhook_subscriptions_file.exists():
        with open(webhook_subscriptions_file, "r") as file:
            lines = file.readlines()

        for line in lines:
            if not line.strip():
                continue
            webhook_sub = WebhookSubscriptionRequest.model_validate_json(line)
            for e in webhook_sub.events:
                if e.name.value == EventName.SUBSTRACT.value:
                    difference = number_pair.a - number_pair.b
                    webhook_response = WebhookPayload(
                        event=EventResponse(name=EventName.SUBSTRACT, id=uuid.uuid1()),
                        description=f"{EventName.SUBSTRACT} event received. Difference of {number_pair.a} and {number_pair.b} is {difference}",
                    )
                    requests.post(
                        webhook_sub.url, json=webhook_response.model_dump(mode="json")
                    )
    return difference


@app.post("/register-webhook", response_model=WebhookSubscriptionResponse)
def register_webhook(webhook_subscription: WebhookSubscriptionRequest):
    webhook_subscriptions_file = Path("webhook_subscriptions.txt")

    if webhook_subscriptions_file.exists():
        with open(webhook_subscriptions_file, "r") as file:
            lines = file.readlines()

        for index, line in enumerate(lines):
            if not line.strip():
                continue
            webhook_sub = WebhookSubscriptionRequest.model_validate_json(line)
            if webhook_subscription.url == webhook_sub.url:
                extra_events = []
                for e in webhook_subscription.events:
                    if e not in webhook_sub.events:
                        extra_events.append(e)

                if len(extra_events) > 0:
                    for event in extra_events:
                        webhook_sub.events.append(event)

                    # rewrite the whole file with webhook_sub updated
                    lines[index] = f"{webhook_sub.model_dump_json()}\n"
                    with open(webhook_subscriptions_file, "w") as file:
                        file.writelines(lines)

                    return WebhookSubscriptionResponse(
                        url=webhook_subscription.url,
                        events=webhook_subscription.events,
                        description=f"{webhook_subscription.url} updated with extra events: {extra_events}",
                    )
                else:
                    raise HTTPException(
                        status_code=202,
                        detail=f"{webhook_subscription.url} already receiving events: {webhook_sub.events}",
                    )
    with open(
        webhook_subscriptions_file, "a"
    ) as file:  # creates webhook_subscriptions.txt if it doesn't exist
        file.write(f"{webhook_subscription.model_dump_json()}\n")

    return WebhookSubscriptionResponse(
        url=webhook_subscription.url,
        events=webhook_subscription.events,
        description=f"Events {webhook_subscription.events} will be now be sent to {
            webhook_subscription.url
        }",
    )


if __name__ == "__main__":
    # with open("webhook_subscriptions.txt", "r") as f:
    #     c = f.read(1)
    #     print(c)
    # print(f.read(1))
    uvicorn.run("publisher:app", host="localhost", port=8000, reload=True)
