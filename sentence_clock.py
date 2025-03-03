from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# Add logger later
class SentenceClock:
    def __init__(self):
        # Define the grid of letters
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

        # Initialize the image
        self.image = Image.new("RGB", (800, 480), "white")  # White background
        self.draw = ImageDraw.Draw(self.image)

        # Load a larger font (replace 'arial.ttf' with the path to your font file)
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/DejaVuSans.ttf", 40)  # Larger font size
        except IOError:
            print("Font file not found. Using default font.")
            self.font = ImageFont.load_default()  # Fallback to default font

        # Update the clock display
        self.update_clock()

        # Export the image as a PNG file
        self.export_as_png()

    def update_clock(self):
        """Update the clock display."""
        # Get the current time
        now = datetime.now()
        hours = now.hour % 12  # Convert to 12-hour format
        minutes = now.minute

        # Draw all letters in black (inactive)
        for i, row in enumerate(self.letters):
            for j, letter in enumerate(row):
                x = j * 60 + 20  # Increased horizontal spacing
                y = i * 50 + 20  # Increased vertical spacing
                self.draw.text((x, y), letter, fill="black", font=self.font)

        # Highlight "IT IS" in red
        self.highlight_letters([(0, 0), (0, 1), (0, 3), (0, 4)], color="red")

        # Highlight minutes in red
        if minutes >= 5 and minutes < 10:
            self.highlight_letters([(2, 0), (2, 1), (2, 2), (2, 3)], color="red")  # FIVE
        elif minutes >= 10 and minutes < 15:
            self.highlight_letters([(0, 9), (0, 10), (0, 11)], color="red")  # TEN
        elif minutes >= 15 and minutes < 20:
            self.highlight_letters([(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)], color="red")  # QUARTER
        elif minutes >= 20 and minutes < 25:
            self.highlight_letters([(1, 7), (1, 8), (1, 9), (1, 10), (1, 11)], color="red")  # TWENTY
        elif minutes >= 25 and minutes < 30:
            self.highlight_letters([(1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, 0), (2, 1), (2, 2), (2, 3)], color="red")  # TWENTY FIVE
        elif minutes >= 30 and minutes < 35:
            self.highlight_letters([(0, 6), (0, 7), (0, 8)], color="red")  # HALF
        elif minutes >= 35 and minutes < 40:
            self.highlight_letters([(1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (2, 0), (2, 1), (2, 2), (2, 3)], color="red")  # TWENTY FIVE
        elif minutes >= 40 and minutes < 45:
            self.highlight_letters([(1, 7), (1, 8), (1, 9), (1, 10), (1, 11)], color="red")  # TWENTY
        elif minutes >= 45 and minutes < 50:
            self.highlight_letters([(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6)], color="red")  # QUARTER
        elif minutes >= 50 and minutes < 55:
            self.highlight_letters([(0, 9), (0, 10), (0, 11)], color="red")  # TEN
        elif minutes >= 55:
            self.highlight_letters([(2, 0), (2, 1), (2, 2), (2, 3)], color="red")  # FIVE

        # Highlight "PAST" or "TO" in red
        if minutes >= 5 and minutes < 35:
            self.highlight_letters([(3, 0), (3, 1), (3, 2), (3, 3)], color="red")  # PAST
        elif minutes >= 35:
            self.highlight_letters([(3, 5), (3, 6)], color="red")  # TO

        # Highlight hours in red
        if minutes >= 35:
            hours += 1  # Round up to the next hour
        if hours == 0:
            hours = 12  # Handle midnight
        self.highlight_hours(hours, color="red")

    def highlight_letters(self, indices, color="red"):
        """Highlight specific letters in the grid."""
        for i, j in indices:
            x = j * 60 + 20  # Increased horizontal spacing
            y = i * 50 + 20  # Increased vertical spacing
            self.draw.text((x, y), self.letters[i][j], fill=color, font=self.font)

    def highlight_hours(self, hour, color="red"):
        """Highlight the current hour."""
        hour_mapping = {
            1: [(4, 0), (4, 1), (4, 2)],  # ONE
            2: [(4, 5), (4, 6), (4, 7)],  # TWO
            3: [(4, 9), (4, 10), (4, 11), (4, 12)],  # THREE
            4: [(5, 0), (5, 1), (5, 2), (5, 3)],  # FOUR
            5: [(5, 4), (5, 5), (5, 6), (5, 7)],  # FIVE
            6: [(6, 0), (6, 1), (6, 2)],  # SIX
            7: [(5, 8), (5, 9), (5, 10), (5, 11), (5, 12)],  # SEVEN
            8: [(6, 4), (6, 5), (6, 6), (6, 7)],  # EIGHT
            9: [(6, 8), (6, 9), (6, 10), (6, 11)],  # NINE
            10: [(7, 0), (7, 1), (7, 2)],  # TEN
            11: [(7, 4), (7, 5), (7, 6), (7, 7), (7, 8), (7, 9)],  # ELEVEN
            12: [(8, 0), (8, 1), (8, 2), (8, 3), (8, 4), (8, 5)],  # TWELVE
        }
        if hour in hour_mapping:
            self.highlight_letters(hour_mapping[hour], color=color)

    def export_as_png(self):
        """Export the image as a PNG file."""
        self.image.save("sentence_clock.png")
        print("Exported sentence_clock.png")

# Run the application
if __name__ == "__main__":
    app = SentenceClock()
