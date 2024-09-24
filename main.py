import fastapi as fp
import sense_hat as sh
import uvicorn

app     = fp.FastAPI()
sense   = sh.SenseHat()

green = (0, 255, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
white = (255,255,255)
nothing = (0,0,0)
pink = (255,105, 180)

W=white
O=nothing


plus = [
    O, O, O, O, O, O, O, O, 
    O, O, O, W, W, O, O, O,
    O, O, O, W, W, O, O, O, 
    O, W, W, W, W, W, W, O,
    O, W, W, W, W, W, W, O,
    O, O, O, W, W, O, O, O,
    O, O, O, W, W, O, O, O,
    O, O, O, O, O, O, O, O
]

@app.get("/")
async def root():
    sense.set_pixels(plus)

@app.get("/reset")
async def reset():
    sense.clear()
    return fp.responses.HTMLResponse(status_code=200)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
