from io import BytesIO

import pytesseract
from PIL import ImageFilter, ImageEnhance
from pdf2image import  convert_from_path


def convert_pdf(path):
    images = convert_from_path(path)
    return "".join(read_image(image) for image in images)


def read_image(image) -> str:
    image = image.convert('L')

    image = image.filter(ImageFilter.MedianFilter())

    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2)

    text = pytesseract.image_to_string(image)

    print(text)
    return text
