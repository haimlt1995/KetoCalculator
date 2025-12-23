import os
import uvicorn

def handler(event, context):
    return {"statusCode": 200, "body": "ok"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
