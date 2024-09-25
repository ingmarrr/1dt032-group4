import fastapi as fp
import fastapi.staticfiles as sf
import sense_hat as sh
import uvicorn

STATIC_DIR="static"

sense   = sh.SenseHat()
app     = fp.FastAPI()

app.mount("/" + STATIC_DIR, sf.StaticFiles(directory=STATIC_DIR), name=STATIC_DIR)

green = (0, 255, 0)
yellow = (255, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
white = (255,255,255)
nothing = (0,0,0)
pink = (255,105, 180)

W=white
O=nothing


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
