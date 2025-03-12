import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from utility import configure_logging

configure_logging()

class SentenceClock:
    def __init__(self):
        self.letters = [
            ['I', 'T', 'R', 'I', 'S', 'U', 'H', 'A', 'L', 'F', 'T', 'E', 'N'],
            ['Q', 'U', 'A', 'R', 'T', 'E', 'R', 'T', 'W', 'E', 'N', 'T', 'Y'],
            ['F', 'I', 'V', 'E', 'Q', 'M', 'I', 'N', 'U', 'T', 'E', 'S', 'T'],
            ['P', 'A', 'S', 'T', 'M', 'T', 'O', 'S', 'A', 'M', 'O', 'P', 'M'],
            ['O', 'N', 'E', 'N', 'T', 'W', 'O', 'Z', 'T', 'H', 'R', 'E', 'E'],
            ['F', 'O', 'U', 'R', 'F', 'I', 'V', 'E', 'S', 'E', 'V', 'E', 'N'],
            ['S', 'I', 'X', 'E', 'I', 'G', 'H', 'T', 'Y', 'N', 'I', 'N', 'E'],
            ['T', 'E', 'N', 'E', 'L', 'E', 'V', 'E', 'N', 'P', 'H', 'I', 'L'],
            ['T', 'W', 'E', 'L', 'V', 'E', 'L', 'O', 'C', 'L', 'O', 'C', 'K'],
        ]
        self.image = Image.new("RGB", (800, 480), "white")
        self.draw = ImageDraw.Draw(self.image)
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", 40)
            logging.info("Font loaded successfully.")
        except IOError:
            logging.warning("Font file not found. Using default font.")
            self.font = ImageFont.load_default()
        self.update_clock()
        self.export_as_png()

    def update_clock(self):
        now = datetime.now()
        hours = now.hour % 12
        minutes = now.minute

        self.draw_all_letters()
        self.highlight_letters([(0, 0), (0, 1), (0, 3), (0, 4)], color="red")  # IT IS

        self.highlight_minutes(minutes)
        self.highlight_past_to(minutes)
        self.highlight_hours(hours, minutes)
        self.highlight_oclock(minutes)

    def draw_all_letters(self):
        for i, row in enumerate(self.letters):
            for j, letter in enumerate(row):
                x = j * 60 + 20
                y = i * 50 + 20
                self.draw.text((x, y), letter, fill="black", font=self.font)

    def highlight_minutes(self, minutes):
        minute_mappings = {
            range(5, 10): [(2, 0), (2, 1), (2, 2), (2, 3)],  # FIVE
            range(10, 15): [(0, 9), (0, 10), (0, 11)],  # TEN
            range(15, 20): [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)],  # QUARTER
            range(20, 25): [(1, 7), (1, 8), (1, 9), (1, 10), (1, 11)],  # TWENTY
            range(25, 30): [(1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, 0), (2, 1), (2, 2), (2, 3)],  # TWENTY FIVE
            range(30, 35): [(0, 6), (0, 7), (0, 8)],  # HALF
            range(35, 40): [(1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, 0), (2, 1), (2, 2), (2, 3)],  # TWENTY FIVE
            range(40, 45): [(1, 7), (1, 8), (1, 9), (1, 10), (1, 11)],  # TWENTY
            range(45, 50): [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)],  # QUARTER
            range(50, 55): [(0, 9), (0, 10), (0, 11)],  # TEN
            range(55, 60): [(2, 0), (2, 1), (2, 2), (2, 3)],  # FIVE
        }
        for minute_range, indices in minute_mappings.items():
            if minutes in minute_range:
                self.highlight_letters(indices, color="red")
                break

    def highlight_past_to(self, minutes):
        if 5 <= minutes < 35:
            self.highlight_letters([(3, 0), (3, 1), (3, 2), (3, 3)], color="red")  # PAST
        elif minutes >= 35:
            self.highlight_letters([(3, 5), (3, 6)], color="red")  # TO

    def highlight_hours(self, hours, minutes):
        if minutes >= 35:
            hours = (hours + 1) % 12
            if hours == 0:
                hours = 12
        hour_mapping = {
            1: [(4, 0), (4, 1), (4, 2)],
            2: [(4, 5), (4, 6), (4, 7)],
            3: [(4, 9), (4, 10), (4, 11), (4, 12)],
            4: [(5, 0), (5, 1), (5, 2), (5, 3)],
            5: [(5, 4), (5, 5), (5, 6), (5, 7)],
            6: [(6, 0), (6, 1), (6, 2)],
            7: [(5, 8), (5, 9), (5, 10), (5, 11), (5, 12)],
            8: [(6, 4), (6, 5), (6, 6), (6, 7)],
            9: [(6, 8), (6, 9), (6, 10), (6, 11)],
            10: [(7, 0), (7, 1), (7, 2)],
            11: [(7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9)],
            12: [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5)],
        }
        self.highlight_letters(hour_mapping[hours], color="red")

    def highlight_oclock(self, minutes):
        if minutes == 0:
            self.highlight_letters([(8, 6), (8, 7), (8, 8), (8, 9), (8, 10), (8, 11), (8, 12)], color="red")

    def highlight_letters(self, indices, color="red"):
        for i, j in indices:
            x = j * 60 + 20  # Increased horizontal spacing
            y = i * 50 + 20  # Increased vertical spacing
            self.draw.text((x, y), self.letters[i][j], fill=color, font=self.font)

    def export_as_png(self):
        self.image.save("sentence_clock.png")
        logging.info("Exported sentence_clock.png")
