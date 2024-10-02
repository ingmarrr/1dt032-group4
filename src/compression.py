import os
import io
from fastapi import FastAPI, File, UploadFile
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from scipy.ndimage import convolve

app = FastAPI()


# Crop the image to a square
def crop_to_square(image):
    width, height = image.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    right = (width + min_dim) // 2
    bottom = (height + min_dim) // 2
    return image.crop((left, top, right, bottom))


# Computing centre alignment
def center_crop(image_array):
    height, width = image_array.shape[0:2]
    # Calculate the new crop area
    min_dim = min(height, width)
    top = (height - min_dim) // 2
    left = (width - min_dim) // 2
    return image_array[top:top + min_dim, left:left + min_dim]


# Enhanced images
def enhance_image(image):
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(1.5)
    return enhanced_image


# Sharpen the image
def sharpen_image(image):
    return image.filter(ImageFilter.SHARPEN)


# Quantify the image
def quantize_image(image):
    quantized_image = image.quantize(colors=8)
    return quantized_image


# Convert images to byte streams
def image_to_bytes(image):
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    return img_byte_arr


# Define the Gaussian kernel
def gaussian_kernel(size=3, sigma=1):
    kernel = np.fromfunction(
        lambda x, y: (1 / (2 * np.pi * sigma ** 2)) *
                      np.exp(-((x - (size - 1) / 2) ** 2 + (y - (size - 1) / 2) ** 2) / (2 * sigma ** 2)),
        (size, size)
    )
    return kernel / np.sum(kernel)

def enhanced_gaussian_kernel(size=5, sigma=1):
    # Create standard Gaussian kernels
    kernel = gaussian_kernel(size=size, sigma=sigma)

    # Increase the weight of the edges
    edge_weight = 1.5  # Weights for edge enhancement
    center_index = size // 2
    kernel[center_index, center_index] *= edge_weight  # Enhancement of centre pixels (edge area)

    return kernel / np.sum(kernel)  # Normalisation

# Downsampling function
def downsample(image):
    # Convert images to arrays
    image_array = np.array(image)

    # Define the Gaussian kernel
    kernel = gaussian_kernel(size=5, sigma=1)

    # Continuous downsampling until close to 8x8
    while image_array.shape[0] > 8 and image_array.shape[1] > 8:
        # Gaussian convolution of images
        image_array = convolve(image_array, kernel[:, :, np.newaxis], mode='reflect')

        # Calculate the size of the new image
        new_shape = (image_array.shape[0] // 2, image_array.shape[1] // 2, image_array.shape[2])
        downsampled_image = np.zeros(new_shape, dtype=image_array.dtype)

        # Perform downsampling
        for i in range(new_shape[0]):
            for j in range(new_shape[1]):
                downsampled_image[i, j] = image_array[i * 2, j * 2]  # Take a pixel every 2 steps as a downsampling value

        # Centre alignment
        downsampled_image = center_crop(downsampled_image)

        image_array = downsampled_image  # Updated to downsampled image

        # Sharpen the image after each downsample
        downsampled_image_pil = Image.fromarray(downsampled_image)
        downsampled_image_pil = sharpen_image(downsampled_image_pil)  # Sharpening
        image_array = np.array(downsampled_image_pil)  # Update to sharpened image

    # Adjust to 8x8, keep centre alignment
    final_image = Image.fromarray(image_array).resize((8, 8), Image.LANCZOS)
    return final_image


# Downsampling function, using double-cubic interpolation
def downsample_bicubic(image):
    # Convert images to arrays
    image_array = np.array(image)

    # Continuous downsampling until close to 8x8
    while image_array.shape[0] > 8 and image_array.shape[1] > 8:
        # Bicubic interpolation downsampling using PIL's resize
        image_pil = Image.fromarray(image_array)
        image_array = np.array(image_pil.resize((image_pil.width // 2, image_pil.height // 2), Image.BICUBIC))

    # Adjusted to 8x8
    final_image = Image.fromarray(image_array).resize((8, 8), Image.LANCZOS)
    return final_image


# The main function that processes the image
def process_image(image, method='downsample'):
    square_image = crop_to_square(image)  # Crop the image to a square
    enhanced_image = enhance_image(square_image)  # Enhanced images
    
    # Downsampling according to specified method
    if method == 'downsample':
        processed_image = downsample(enhanced_image)  # Use Gaussian downsampling
    elif method == 'bicubic':
        processed_image = downsample_bicubic(enhanced_image)  # Downsampling using double cubic interpolation
    else:
        raise ValueError("Unsupported methods, please select 'downsample'、'bicubic' 或 'laplacian'")
    sharpened_image = sharpen_image(processed_image)  # Sharpen the image before quantising
    quantized_image = quantize_image(sharpened_image)  # Perform colour quantification
    return quantized_image

# Routing of uploaded images
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...), method: str = 'downsample'):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))  # Getting images from the front end

    # Crop the image to a square
    image = crop_to_square(image)  # Cropped to a square

    quantized_image = process_image(image, method=method)  # Processing images
    output_image_bytes = image_to_bytes(quantized_image)  # Convert to byte stream to return

    return {"processed_image": output_image_bytes}

# Functions to handle local images
def process_local_image(image_name, method='downsample'):
    input_path = os.path.join("Image", "Input", image_name)
    output_path = os.path.join("Image", "Output", f"processed_{method}_{image_name}")

    if not os.path.isfile(input_path):
        return {"error": "Input image does not exist"}

    image = Image.open(input_path)  # Read the local image

    # Crop the image to a square
    image = crop_to_square(image)  # Cropped to a square

    quantized_image = process_image(image, method=method)  # Processing images
    # Save processed images
    quantized_image.save(output_path)

    # Size of output image
    print(f"Image size after cropping: {image.size}")
    print(f"Size of processed image: {quantized_image.size}")

    return {"message": f"Processing is complete and has been saved to {output_path}"}

# main function
if __name__ == "__main__":
    # Test processed image names and downsampling methods
    image_names = ["Smile.png", "Apple.png", "Dog.png", "Mountain.png", "Flower.png", "Heart.png"]  # Replace it with your actual image file name
    methods = ['downsample', 'bicubic']  # Optional downsampling methods

    for image_name in image_names:
        for method in methods:
            print(f"process image {image_name} Usage {method}...")
            result = process_local_image(image_name, method=method)
            print(result)
