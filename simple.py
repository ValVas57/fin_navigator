print("Server starting...")
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok"}

if __name__ == "__main__":
    print("Running on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)