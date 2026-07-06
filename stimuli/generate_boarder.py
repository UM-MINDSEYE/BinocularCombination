import numpy as np
from PIL import Image

# --- Settings ---
img_size = 512          # final image size (pixels)
square_size = 32        # size of each checker square
border_thickness = 2    # number of squares in border
bg_color = 128          # gray background (0–255)

# --- Create base image ---
img = np.full((img_size, img_size), bg_color, dtype=np.uint8)

# Number of squares per side
n = img_size // square_size

for x in range(n):
    for y in range(n):

        # Check if we're in the border region
        if (
            x < border_thickness or x >= n - border_thickness or
            y < border_thickness or y >= n - border_thickness
        ):
            # Checker pattern
            if (x + y) % 2 == 0:
                color = 0      # black
            else:
                color = 255    # white

            # Fill square
            x0 = x * square_size
            y0 = y * square_size
            img[y0:y0+square_size, x0:x0+square_size] = color

# --- Save image ---
image = Image.fromarray(img)
image.save("checker_border.png")

print("Saved as checker_border.png")