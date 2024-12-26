import cv2
import numpy as np

def create_binary_image(filename):
    # Load the image
    img = cv2.imread(filename)
    if img is None:
        raise FileNotFoundError(f"File {filename} not found.")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Apply GaussianBlur to reduce noise
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    # Apply morphological closing to enhance the edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Combine the edges with the original enhanced image
    combined = cv2.addWeighted(closed_edges, 0.8, enhanced, 0.2, 0)

    # Apply threshold to create binary image
    _, binary = cv2.threshold(combined, 200, 255, cv2.THRESH_BINARY)

    # Save and display the binary image
    output_filename = "binary_parking_lot_final.png"
    cv2.imwrite(output_filename, binary)

    cv2.imshow('Binary Image - Final', binary)
    k = cv2.waitKey(0)
    cv2.destroyAllWindows()

    return output_filename

# Create binary image
filename = "parking-lot.png"  # Replace with your file path
output_file = create_binary_image(filename)
print(f"Binary image saved at {output_file}")
