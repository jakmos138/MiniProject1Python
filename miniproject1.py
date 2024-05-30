import requests
from PIL import Image
from io import BytesIO

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        return Image.open(BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
        return None
    except IOError as e:
        print(f"Error opening the image: {e}")
        return None

url1 = "https://cdn.thecollector.com/wp-content/uploads/2023/04/hp-lovecraft-cthulhu-mythos.jpg?width=1400&quality=55"
img1 = download_image(url1)
if img1 is None:
    raise SystemExit("Failed to download Picture #1")

original_width, original_height = img1.size
new_width, new_height = 1000, 700

left = (original_width - new_width) / 2
top = (original_height - new_height) / 2
right = (original_width + new_width) / 2
bottom = (original_height + new_height) / 2

crop_box = (left, top, right, bottom)
img1_cropped = img1.crop(crop_box)

resize_dimensions = (1000, 700)
img1_resized = img1_cropped.resize(resize_dimensions)

url2 = "https://cdn-icons-png.flaticon.com/128/1136/1136964.png"
img2 = download_image(url2)
if img2 is None:
    raise SystemExit("Failed to download Picture #1")

# Rotate the image by a chosen angle
angle = 45  # Example value
img2_rotated = img2.rotate(angle, expand=True)

offset_x = 350  # Example offset value
offset_y = 150  # Example offset value
position = ((img1_cropped.width - img2_rotated.width) // 2 + offset_x, 
            (img1_cropped.height - img2_rotated.height) // 2 + offset_y)

# Create a new image to avoid modifying the original
final_image = img1_cropped.copy()
final_image.paste(img2_rotated, position, img2_rotated)

# Save the final image
final_image.save("final_image.png")

# Optionally, display the final image
final_image.show()
