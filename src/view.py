import fastapi as fp
import main

@main.app.get("/reset")
async def reset():
    main.sense.clear()
    return fp.responses.HTMLResponse(status_code=200)

@main.app.get("/")
async def root():

    return """
        <div class="p_title">1DT032 Project - Group 4</div>
    """

@main.app.post("/upload")
async def upload(file: fp.UploadFile):

    return f"""
        <div class="p_result_success">
            <div class="p_title">Upload successful!</div>
            <div class="p_subtitle">{file.filename}</div>
        </div>
    """


if __name__ == "__main__":
    pass
