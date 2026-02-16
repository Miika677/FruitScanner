#https://gs1.fi/fi/standardit/yksiloinnin-standardit/tuotetunniste-gtin
#https://e-kassa.fi/tuotteet/vaihtuvamittainen-vaihtuvapainoinen-muuttuva-viivakoodi-punnittavat-tuotteet-gtin
#For information on how GTIN-13 codes are formed.

from labels import fruitids, priceperkg #Dict with IDs for the fruits.

#GTIN generation

def generate_gtin_by_price(fruit : str, weight : int) -> str:
    prefix = "2000"
    #Prefix is 20 00 for items with varying weight (fruits, vegetables).
    #GTIN structure changes depending on the chosen attribute ie. weight or price.
    product_id = f"{fruitids[fruit]:04d}"
    price_cents = f"{round((weight / 1000) * priceperkg[fruit]):04d}"

    gtin12 = prefix + product_id + price_cents

    return gtin12 + check_digit(gtin12)

def check_digit(gtin12 : str) -> str:
    #check digit algorithm
    total = 0
    for i, num in enumerate(gtin12, start=1):
        n = int(num)
        if i % 2 == 0:
            total += n * 3
        else:
            total += n * 1
    return str((10 - (total % 10)) % 10)

#Barcode & Sticker creation

import time
from io import BytesIO
from barcode import EAN13
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont

#Memory only barcode image
def create_barcode_image_buffer(fruit : str, weight : int) -> Image.Image:
    buffer = BytesIO()
    EAN13(generate_gtin_by_price(fruit, weight), writer=ImageWriter()).write(buffer)
    return Image.open(buffer)

#Sticker creation
def create_price_sticker(
    store_name: str,
    fruit: str,
    weight_grams: int,
    output_path: str):

    label = Image.new("1", (400, 300), "white")
    draw = ImageDraw.Draw(label)

    #Fonts
    title_font = ImageFont.load_default(22)
    text_font = ImageFont.load_default(12)

    #Store name
    draw.text((20, 10), store_name.upper(), fill="black", font=title_font)

    #Product name
    draw.text((20, 60), fruit.upper(), fill="black", font=text_font)

    #Eur/kg text
    draw.text((20, 80), f"{priceperkg[fruit] / 100:.2f} EUR/kg".replace('.', ','), fill="black", font=text_font)

    #Weight text
    weight_kg = weight_grams / 1000
    draw.text((20, 100), f"Weight: {weight_kg:.2f} kg".replace('.', ','), fill="black", font=text_font)

    #Final price text
    price_cents = round((weight_kg) * priceperkg[fruit])
    draw.text((20, 120), f"{price_cents / 100:.2f} EUR".replace('.', ','), fill="black", font=title_font)

    #Barcode
    barcode_img = create_barcode_image_buffer(fruit, weight_grams)
    barcode_img = barcode_img.resize((300, 100))
    label.paste(barcode_img, (50, 180))

    #Timestamp
    date = time.strftime("%d.%m.%Y %H:%M", time.localtime())
    draw.text((200, 180), date, fill="black", font=text_font, anchor="ms")

    #Save label to disk and return to render template
    label.save(output_path)
    return output_path
