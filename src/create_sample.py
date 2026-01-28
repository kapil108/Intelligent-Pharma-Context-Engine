import cv2
import numpy as np

def create_sample_image():
    # Create white image
    img = np.ones((500, 500, 3), dtype=np.uint8) * 255
    
    # Add Text: Drug Name
    cv2.putText(img, "Lisinopril", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    # Add Text: Dosage
    cv2.putText(img, "10 mg", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Add Mock Barcode (Lines)
    for i in range(10):
        cv2.rectangle(img, (50 + i*20, 400), (60 + i*20, 480), (0, 0, 0), -1)

    # Add artificial glare (white circle with blur)
    overlay = img.copy()
    cv2.circle(overlay, (250, 250), 100, (255, 255, 255), -1)
    cv2.addWeighted(overlay, 0.4, img, 0.6, 0, img)
    
    # Save
    output_path = "repo/data/sample/test_bottle.jpg"
    cv2.imwrite(output_path, img)
    print(f"Created sample image at {output_path}")

if __name__ == "__main__":
    create_sample_image()
