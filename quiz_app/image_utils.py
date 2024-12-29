from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

def resize_image(image, max_width, max_height):
    if isinstance(image, InMemoryUploadedFile):
        img = Image.open(image)
    elif isinstance(image, str):
        img = Image.open(image)
    else:
        return image

    aspect_ratio = img.width / img.height
    new_width = min(img.width, max_width)
    new_height = int(new_width / aspect_ratio)

    if new_height > max_height:
        new_height = max_height
        new_width = int(new_height * aspect_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Ottimizza l'immagine
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85, optimize=True)
    return InMemoryUploadedFile(buffer, None, 'resized_image.jpg', 'image/jpeg', buffer.getbuffer().nbytes, None)