import fastapi as fp
import sense_hat as sh
import uvicorn

app     = fp.FastAPI()
sense   = sh.SenseHat()

@app.get("/")
async def root():
    return { "message": "Moin" }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
