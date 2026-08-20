import uvicorn
from fastapi import FastAPI

from publisher import WebhookPayload

app = FastAPI()


@app.post("/webhook")
def webhook(webhook_payload: WebhookPayload):
    with open("received_events.txt", "a") as file:
        file.write(f"{webhook_payload.model_dump_json()}\n")
    return f"Received webhook payload: {webhook_payload}"


if __name__ == "__main__":
    uvicorn.run("subscriber:app", host="localhost", port=8001, reload=True)
