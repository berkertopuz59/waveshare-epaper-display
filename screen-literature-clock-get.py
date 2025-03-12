import random
import codecs
import textwrap
from utility import is_stale, configure_logging
import requests
import csv
import datetime
import re
import math
from PIL import Image, ImageDraw, ImageFont
import logging

configure_logging()

def main():
    if is_stale('litclock_annotated.csv', 86400):
        url = "https://raw.githubusercontent.com/JohannesNE/literature-clock/master/litclock_annotated.csv"
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open('litclock_annotated.csv', 'w') as text_file:
                text_file.write(response.text)
            logging.info("litclock_annotated.csv updated successfully.")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch or save litclock_annotated.csv: {e}")
            exit()
    
    time_rows = []
    current_time = datetime.datetime.now().strftime("%H:%M")
    with open('litclock_annotated.csv', 'r') as file:
        reader = csv.DictReader(file,
                                fieldnames=[
                                    "time", "time_human", "full_quote", "book_title", "author_name", "sfw"],
                                delimiter='|',
                                lineterminator='\n',
                                quotechar=None, quoting=csv.QUOTE_NONE)
        for row in reader:
            if row["time"] == current_time:
                time_rows.append(row)
    
    
    if len(time_rows) == 0:
        logging.error("No quotes found for this time.")
        exit()
    else:
        chosen_item = min(time_rows, key=lambda x: len(x["full_quote"]))
        logging.info(f"Chosen quote: {chosen_item}")
        quote = chosen_item["full_quote"]
        book = chosen_item["book_title"]
        author = chosen_item["author_name"]
        human_time = chosen_item["time_human"]
    
    # replace newlines with spaces
    quote = quote.replace("<br/>", " ")
    quote = quote.replace("<br />", " ")
    quote = quote.replace("<br>", " ")
    quote = quote.replace(u"\u00A0", " ")  # non breaking space
    
    # replace punctuation with simpler counterparts
    transl_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´“”—–-",  u"'''\"\"---")])
    quote = quote.translate(transl_table)
    human_time = human_time.translate(transl_table)
    quote = quote.encode('ascii', 'ignore').decode('utf-8')
    human_time = human_time.encode('ascii', 'ignore').decode('utf-8')
    
    quote_length = len(quote)
    
    # Try to calculate font size and max chars based on quote length
    goes_into = (quote_length / 100) if quote_length > 80 else 0
    font_size = 60 - (goes_into * 8)
    max_chars_per_line = 23 + (goes_into * 6)
    
    # Some upper and lower limit adjustments
    font_size = 25 if font_size < 25 else font_size
    max_chars_per_line = 55 if max_chars_per_line > 55 else max_chars_per_line
    
    font_size = math.ceil(font_size)
    max_chars_per_line = math.floor(max_chars_per_line)
    
    attribution = f"- {book}, {author}"
    if len(attribution) > 55:
        attribution = attribution[:55] + "…"
    
    logging.info(f"Quote length: {quote_length}, Font size: {font_size}, Max chars per line: {max_chars_per_line}")
    
    quote_pattern = re.compile(re.escape(human_time), re.IGNORECASE)
    # Replace human time by itself but surrounded by pipes for later processing.
    quote = quote_pattern.sub(lambda x: f"|{x.group()}|", quote, count=1)
    
    lines = textwrap.wrap(quote, width=max_chars_per_line, break_long_words=True)
    
    # Image Generation
    image_width = 800
    image_height = 480
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)
    
    # Font loading
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", 40)
        attribution_font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", 30)
    except OSError as e:
        logging.error(f"Failed to load font: {e}. Using default font.")
        font = ImageFont.load_default()
        attribution_font = ImageFont.load_default()
    y_offset = 15
    x_offset = 33
    
    time_ends_on_next_line = False
    for line in lines:
        try:
            if line.count("|") == 2:
                parts = line.split("|")
                draw.text((x_offset, y_offset), parts[0], font=font, fill="black")
                text_width = draw.textlength(parts[0], font=font)
                draw.text((x_offset + text_width, y_offset), parts[1], font=font, fill="red")
                text_width += draw.textlength(parts[1], font=font)
                draw.text((x_offset + text_width, y_offset), parts[2], font=font, fill="black")
            elif line.count("|") == 1 and not time_ends_on_next_line:
                parts = line.split("|")
                draw.text((x_offset, y_offset), parts[0], font=font, fill="black")
                text_width = draw.textlength(parts[0], font=font)
                draw.text((x_offset + text_width, y_offset), parts[1], font=font, fill="red")
                time_ends_on_next_line = True
            elif line.count("|") == 1 and time_ends_on_next_line:
                draw.text((x_offset, y_offset), line.replace("|", ""), font=font, fill="red")
                time_ends_on_next_line = False
            else:
                draw.text((x_offset, y_offset), line, font=font, fill="black")
    
            y_offset += font.getbbox(line)[3] * 1.2  # Adjust line spacing
        except Exception as e:
            logging.error(f"Error processing line '{line}': {e}")
    
    # Draw attribution
    attribution_x = 150
    attribution_y = y_offset + font.getbbox(lines[0])[3] * 1.5
    draw.text((attribution_x, attribution_y), attribution, font=attribution_font, fill="black")
    
    # Save the image
    output_png_filename = 'screen-literature-clock.png'
    try:
        image.save(output_png_filename)
        logging.info(f"Image saved as {output_png_filename}")
    except Exception as e:
        logging.error(f"Failed to save image: {e}")

if __name__ == "__main__":
    main()
