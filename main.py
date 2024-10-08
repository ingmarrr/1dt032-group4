import fastapi as fp
import fastapi.staticfiles as sf
from fastapi.templating import Jinja2Templates
import sense_hat as sh
import uvicorn

from pathlib import Path

STATIC_DIR="static"

sense   = sh.SenseHat()
app     = fp.FastAPI()

app.mount("/" + STATIC_DIR, sf.StaticFiles(directory=STATIC_DIR), name=STATIC_DIR)

base_dir = Path(__file__).resolve().parent
app.mount(
    "/static",
    sf.StaticFiles(directory=base_dir / "static"), 
    name="static"
)

templ = Jinja2Templates(directory="./static/templates")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
