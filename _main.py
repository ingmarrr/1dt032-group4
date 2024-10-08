import fastapi as fp
import fastapi.staticfiles as sf
from fastapi.templating import Jinja2Templates
import uvicorn
from pathlib import Path

app     = fp.FastAPI()

class sense:
    """
    Placeholder for actual sense
    """
    @staticmethod
    def clear():
        print("clearing sense-hat")
        pass

base_dir = Path(__file__).resolve().parent
app.mount(
    "/static",
    sf.StaticFiles(directory=base_dir / "static"), 
    name="static"
)

templ = Jinja2Templates(directory="./static/templates")

if __name__ == "__main__":
    import src.api
    uvicorn.run("_main:app", host="0.0.0.0", port=8000)
