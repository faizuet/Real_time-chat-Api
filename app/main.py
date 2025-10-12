from fastapi import FastAPI

app = FastAPI(title="Chatly API", version="1.0.0")

@app.get("/")
async def read_root():
    return {"message": "Welcome to Chatly API!"}

