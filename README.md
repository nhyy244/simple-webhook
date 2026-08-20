# Simple webhook 
The purpose of this project was to familiriaze myself more with webhooks. It consits of two small FastAPI apps, publisher and subscriber. 
Publisher has three endpoints `\add`, `\substract`, and `\register_webhook`. Add and substract are meant to mimic the logic of an app and the purpose of `register_webhook` is for another service to subscribe and receive events whenever that logic triggers. 

## Try it out
Install packages
```python
uv sync
```  
Run both publisher and subscriber servers: 
```python
source .venv/bin/activate
python publisher.py
python subscriber.py
```
Subscribe to the publisher: 
```bash
curl -X POST http://localhost:8000/register-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://localhost:8001/webhook",
    "events": [{"name": "add"}, {"name": "substract"}]
  }'
```
The subscriptions are saved in `webhook_subscriptions.txt` in the root of the project. 

Now send some requests to `/add` and `/substract`.
```bash
curl -X POST http://localhost:8000/add \
  -H "Content-Type: application/json" \
  -d '{"a": 3, "b": 4}'
  curl -X POST http://localhost:8000/substract \
  -H "Content-Type: application/json" \
  -d '{"a": 3, "b": 4}'
```
The events are saved in `received_events.txt` in the root of the project. 

