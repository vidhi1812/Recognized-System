import cv2

def rectangle(img, faceLoc, name):
    y1, x2, y2, x1 = faceLoc  # Correct order
    y1, x1, y2, x2 = y1 * 4, x1 * 4, y2 * 4, x2 * 4  # Scale back to original size
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
