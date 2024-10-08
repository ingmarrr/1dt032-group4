import fastapi as fp
from sense_hat import SenseHat
import PIL.Image as img

import io

import main
import src.compression as cp

# Draw the image on the Sense HAT LED matrix
def draw_image_on_led_matrix(image: img.Image) -> str | None:
    image       = image.resize((8, 8), img.LANCZOS)
    image_rgb   = image.convert("RGB")
    pixel_data  = list(image_rgb.getdata())

    if len(pixel_data) != 64:
        return f"failed image resizing. Expected 64 found size {len(pixel_data)}."

    main.sense.set_pixels(pixel_data)


def process_and_draw_image(file_contents, method='downsample') -> str | None:
    image       = img.open(io.BytesIO(file_contents)) 
    processed   = cp.process_image(image, method=method)
    if processed is None:
        return "failed to process image"

    # Draw the compressed 8x8 image on the Sense HAT
    draw_image_on_led_matrix(processed)


@main.app.post("/upload-and-draw")
async def upload_and_draw(file: fp.UploadFile, method: str = 'downsample'):
    contents = await file.read()
    process_and_draw_image(contents, method=method)

    return {"message": "Image has been processed and displayed on the Raspberry Pi's LED matrix."}

if __name__ == "__main__":
    pass
