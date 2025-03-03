import sys
import os
import logging
import datetime
from PIL import Image
from utility import configure_logging

libdir = "./lib/e-Paper/RaspberryPi_JetsonNano/python/lib"
if os.path.exists(libdir):
    sys.path.append(libdir)

configure_logging()

# Define thresholds
red_threshold = 150  # Adjust based on your image
black_threshold = 150  # Adjust based on your image

waveshare_epd75_version = os.getenv("WAVESHARE_EPD75_VERSION", "2B")

if waveshare_epd75_version == "1":
    from waveshare_epd import epd7in5 as epd7in5
elif waveshare_epd75_version == "2B":
    from waveshare_epd import epd7in5b_V2 as epd7in5
else:
    from waveshare_epd import epd7in5_V2 as epd7in5

try:
    epd = epd7in5.EPD()
    logging.debug("Initialize screen")
    epd.init()

    # Full screen refresh at 2 AM
    if datetime.datetime.now().minute == 0 and datetime.datetime.now().hour == 2:
        logging.debug("Clear screen")
        epd.Clear()

    filename = sys.argv[1]

    logging.debug("Read image file: " + filename)
    Himage = Image.open(filename)

    # Ensure the image is in RGB mode
    if Himage.mode != 'RGB':
        Himage = Himage.convert('RGB')

    logging.info("Display image file on screen")

    if waveshare_epd75_version == "2B":
        # Handle red color for "B" version displays
        Limage_Black = Image.new('1', (Himage.width, Himage.height), 255)  # Black channel
        Limage_Red = Image.new('1', (Himage.width, Himage.height), 255)  # Red channel

        # Convert the image to black and red components
        for x in range(Himage.width):
            for y in range(Himage.height):
                pixel = Himage.getpixel((x, y))
                r, g, b = pixel  # Extract the RGB components of the pixel

                # Log pixel values for debugging
                logging.debug(f"Pixel at ({x}, {y}): R={r}, G={g}, B={b}")

                # Detect red shades (red is dominant)
                if r > g + red_threshold and r > b + red_threshold:  # Red dominant
                    Limage_Red.putpixel((x, y), 0)  # Set red in red channel
                # Detect black shades (all channels are close to 0)
                elif r <= black_threshold and g <= black_threshold and b <= black_threshold:
                    Limage_Black.putpixel((x, y), 0)  # Set black in black channel
                else:  # For all other colors (e.g., white or light colors)
                    Limage_Black.putpixel((x, y), 255)  # Set white in black channel
                    Limage_Red.putpixel((x, y), 255)    # Set white in red channel
        
        epd.display(epd.getbuffer(Limage_Black), epd.getbuffer(Limage_Red))
    else:
        epd.display(epd.getbuffer(Himage))
    epd.sleep()

except IOError as e:
    logging.exception(e)

except KeyboardInterrupt:
    logging.debug("Keyboard Interrupt - Exit")
    epd7in5.epdconfig.module_exit()
    exit()
