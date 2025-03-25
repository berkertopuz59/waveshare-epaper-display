import textwrap
import requests
import csv
import datetime
import re
from PIL import Image, ImageDraw, ImageFont
import logging
from utility import is_stale, configure_logging

configure_logging()

# Constants
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 480
FONT_PATH = "/usr/share/fonts/truetype/NotoSans-Regular.ttf"

def get_quote():
    """Fetch the current time's quote from the CSV file."""
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
            return None

    current_time = datetime.datetime.now().strftime("%H:%M")
    with open('litclock_annotated.csv', 'r') as file:
        reader = csv.DictReader(file, fieldnames=["time", "time_human", "full_quote", "book_title", "author_name", "sfw"],
                                delimiter='|', lineterminator='\n', quotechar=None, quoting=csv.QUOTE_NONE)
        quotes = [row for row in reader if row["time"] == current_time]

    if not quotes:
        logging.error("No quotes found for this time.")
        return None

    # Choose the shortest quote to fit in the image
    return min(quotes, key=lambda x: len(x["full_quote"]))

def clean_quote(quote, human_time):
    """Clean up quote text and highlight the time."""\
    # replace newlines with spaces
    quote = re.sub(r"<br\s*/?>", " ", quote)  # Handles <br>, <br/>, <br /> etc.
    #quote = re.sub(r"[\u2018\u2019\u02BB\u02BC\u02BD\u0060]", "'", quote)  # Various single quotes
    #quote = re.sub(r"[\u201C\u201D]", '"', quote)  # Various double quotes
    quote = re.sub(r"\u00A0", " ", quote)  # Non-breaking space

    # Replace the human-readable time in the quote with markers for styling
    time_highlight = re.compile(re.escape(human_time), re.IGNORECASE)
    quote = time_highlight.sub(lambda x: f"|{x.group()}|", quote, count=1)

    return quote

def calculate_font_size(quote):
    """Dynamically calculate font size based on quote length."""
    length_factor = min(max(len(quote) / 120, 0.5), 1.2)  # Adjust scale factor
    font_size = max(25, int(50 - (length_factor * 15)))
    return font_size

def create_image(quote, attribution, human_time):
    """Generate an image with the quote displayed dynamically."""
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), "white")
    draw = ImageDraw.Draw(image)

    # Load fonts
    try:
        font_size = calculate_font_size(quote)
        font = ImageFont.truetype(FONT_PATH, font_size)
        attribution_font = ImageFont.truetype(FONT_PATH, font_size - 5)
    except OSError:
        logging.error("Failed to load custom font. Using default font.")
        font = ImageFont.load_default()
        attribution_font = ImageFont.load_default()

    # Word wrapping based on image width
    max_width = IMAGE_WIDTH - 100
    lines = []
    for paragraph in quote.split("\n"):
        lines.extend(textwrap.wrap(paragraph, width=40))  # Adjust for better fit

    # Calculate vertical centering
    total_text_height = sum([font.getbbox(line)[3] for line in lines]) * 1.2
    y_offset = (IMAGE_HEIGHT - total_text_height) // 2 - 20

    # Render text
    for line in lines:
        x_offset = (IMAGE_WIDTH - draw.textlength(line, font=font)) // 2  # Center text
        if "|" in line:  # Highlight human time in red
            parts = line.split("|")
            draw.text((x_offset, y_offset), parts[0], font=font, fill="black")
            text_width = draw.textlength(parts[0], font=font)
            draw.text((x_offset + text_width, y_offset), parts[1], font=font, fill="red")
            text_width += draw.textlength(parts[1], font=font)
            draw.text((x_offset + text_width, y_offset), parts[2], font=font, fill="black")
        else:
            draw.text((x_offset, y_offset), line, font=font, fill="black")
        y_offset += font.getbbox(line)[3] * 1.2  # Adjust spacing

    # Draw attribution
    attribution_x = (IMAGE_WIDTH - draw.textlength(attribution, font=attribution_font)) // 2
    draw.text((attribution_x, y_offset + 10), attribution, font=attribution_font, fill="black")

    # Save image
    output_filename = "screen-literature-clock.png"
    try:
        image.save(output_filename, optimize=True, compress_level=0)
        logging.info(f"Image saved as {output_filename}")
    except Exception as e:
        logging.error(f"Failed to save image: {e}")

def main():
    chosen_item = get_quote()
    if not chosen_item:
        return

    quote = clean_quote(chosen_item["full_quote"], chosen_item["time_human"])
    attribution = f"- {chosen_item['book_title']}, {chosen_item['author_name']}"
    create_image(quote, attribution, chosen_item["time_human"])

if __name__ == "__main__":
    main()
