import uvicorn
from fastapi import FastAPI

from publisher import WebhookPayload

app = FastAPI()


@app.post("/webhook")
def webhook(webhook_payload: WebhookPayload):
    return None


if __name__ == "__main__":
    uvicorn.run("subscriber:app", host="localhost", port=8001, reload=True)
