import io
import base64
from typing import Optional

import fastapi as fp
import fastapi.responses as res
import PIL.Image as img

import main as main

import src.compression as cp
import src.draw as draw

@main.app.get("/")
async def root(req: fp.Request): 
    try:
        return main.templ.TemplateResponse(
            "index.html", 
            {"request":req}
        )
    except Exception as e:
        raise fp.HTTPException(status_code=500, detail=str(e))

@main.app.get("/upload")
async def g_upload(req: fp.Request):
    try: 
        return main.templ.TemplateResponse(
            "upload.html",
            {"request":req}
        )
    except Exception as e:
        raise fp.HTTPException(status_code=500, detail=str(e))

@main.app.get("/draw")
async def g_draw(req: fp.Request):
    try: 
        return main.templ.TemplateResponse(
            "draw.html",
            {"request":req}
        )
    except Exception as e:
        raise fp.HTTPException(status_code=500, detail=str(e))


@main.app.post("/upload")
async def p_upload(file: fp.UploadFile):
    try:
        content = await file.read()
        if isinstance(content, str):
            content = content.encode("utf-8")
        image   = img.open(io.BytesIO(content))

        processed = cp.process_image(image, "downsample")
        if processed is None:
            return None
        
        result = draw.draw_image_on_led_matrix(processed)
        if isinstance(result, str):
            return res.RedirectResponse(url=f"/error?{result}")

        image_bytes = cp.image_to_bytes(processed)
        out         = base64.b64encode(image_bytes).decode("utf-8")

        return res.HTMLResponse(f"""
            <div class="p_result_success flex flex-col items-center">
                <div class="p_title">Upload successful!</div>
                <div class="p_subtitle">{file.filename}</div>
                <img src="data:image/png;base64,{out}" alt="Image" style="width: 500px; height: auto;">
            </div>
        """, status_code=200)
    except Exception as e:
        print(str(e))
        raise fp.HTTPException(status_code=500, detail=str(e))

@main.app.get("/error")
async def error(req: fp.Request, msg: str):
    try: 
        return main.templ.TemplateResponse(
            "error.html",
            {
                "request": req,
                "msg": msg
            }
        )
    except Exception as e:
        raise fp.HTTPException(status_code=500, detail=str(e))

@main.app.get("/api/reset")
async def g_reset():
    main.sense.clear()
    return fp.responses.HTMLResponse(status_code=200)


@main.app.post("/api/upload")
async def api_post_upload(file: fp.UploadFile):
    try:
        out = process_and_encode_file(file)
        if out is None:
            return res.RedirectResponse(url=f"/error?failed processing image")

        return {"img": out}

    except Exception as e:
        print(str(e))
        raise fp.HTTPException(status_code=500, detail=str(e))
        
async def process_and_encode_file(file: fp.UploadFile, method="downsample") -> Optional[str]:
    content = await file.read()
    if isinstance(content, str):
        content = content.encode("utf-8")
    image   = img.open(io.BytesIO(content))

    processed = cp.process_image(image, method)
    if processed is None:
        return None
    
    image_bytes = cp.image_to_bytes(processed)
    return base64.b64encode(image_bytes).decode("utf-8")


if __name__ == "__main__":
    pass
