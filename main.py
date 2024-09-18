import fastapi as fp

app = fp.FastAPI()

@app.get("/")
async def root():
    return { "message": "Moin" }
