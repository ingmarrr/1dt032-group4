from sense_hat import SenseHat
from PIL import Image
import numpy as np

sense = SenseHat()


# Draw the image on the Sense HAT LED matrix
def draw_image_on_led_matrix(image):
    # Resize the image to 8x8 just in case it's not already
    image = image.resize((8, 8), Image.LANCZOS)

    # Convert the image to RGB (even if it's quantized)
    image_rgb = image.convert("RGB")

    # Get pixel data as a list of (R, G, B) tuples
    pixel_data = list(image_rgb.getdata())

    # Make sure there are exactly 64 pixels for the Sense HAT (8x8)
    if len(pixel_data) != 64:
        raise ValueError("The image is not 8x8 and cannot be displayed on the LED matrix.")

    # Send the pixel data to the Sense HAT
    sense.set_pixels(pixel_data)


# Example to process and draw an uploaded image
def process_and_draw_image(file_contents, method='downsample'):
    image = Image.open(io.BytesIO(file_contents))  # Get the image from file contents
    quantized_image = process_image(image, method=method)  # Process and compress the image (from your previous code)

    # Draw the compressed 8x8 image on the Sense HAT
    draw_image_on_led_matrix(quantized_image)


# FastAPI endpoint to upload an image and display it on the Sense HAT
@app.post("/upload-and-draw/")
async def upload_and_draw(file: UploadFile = File(...), method: str = 'downsample'):
    contents = await file.read()
    process_and_draw_image(contents, method=method)

    return {"message": "Image has been processed and displayed on the Raspberry Pi's LED matrix."}
