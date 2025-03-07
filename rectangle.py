import cv2
import numpy as np

class ROISelector:
    def __init__(self):
        self.roi = None
        self.dragging = False
        self.start_pos = None
        self.current_pos = None

    def select_roi(self, window_name, frame):
        """Allow user to select ROI by dragging mouse"""
        cv2.namedWindow(window_name)
        cv2.setMouseCallback(window_name, self._mouse_callback)
        
        clone = frame.copy()
        while True:
            image = clone.copy()
            if self.start_pos and self.current_pos:
                cv2.rectangle(image, self.start_pos, self.current_pos, (0, 255, 0), 2)
            
            cv2.imshow(window_name, image)
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('c'):  # Press 'c' to confirm selection
                break
        
        if self.start_pos and self.current_pos:
            x1, y1 = min(self.start_pos[0], self.current_pos[0]), min(self.start_pos[1], self.current_pos[1])
            x2, y2 = max(self.start_pos[0], self.current_pos[0]), max(self.start_pos[1], self.current_pos[1])
            self.roi = (x1, y1, x2 - x1, y2 - y1)  # x, y, width, height
        
        cv2.destroyWindow(window_name)
        return self.roi

    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.start_pos = (x, y)
            self.current_pos = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.current_pos = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.dragging = False
            self.current_pos = (x, y)

def draw_face_rectangle(img, faceLoc, name, is_entry=True, roi=None):
    """
    Draw rectangle and name for detected face with proper scaling
    
    Args:
        img: Input image
        faceLoc: Face location tuple (top, right, bottom, left)
        name: Name to display
        is_entry: Boolean to determine color (green for entry, red for exit)
        roi: ROI tuple (x, y, width, height) if using ROI
    """
    # Get image dimensions
    img_height, img_width = img.shape[:2]
    
    # Extract face location coordinates
    top, right, bottom, left = faceLoc
    
    # If using ROI, adjust coordinates
    if roi:
        x_offset, y_offset = roi[0], roi[1]
        left += x_offset
        right += x_offset
        top += y_offset
        bottom += y_offset
    
    # Calculate scaling factors
    scale_x = img_width / 640  # Assuming detection on 640x480
    scale_y = img_height / 480
    
    # Scale coordinates to match image size
    left = int(left * scale_x)
    right = int(right * scale_x)
    top = int(top * scale_y)
    bottom = int(bottom * scale_y)
    
    # Set colors (BGR format)
    rect_color = (0, 255, 0) if is_entry else (0, 0, 255)  # Green for entry, Red for exit
    text_color = (255, 255, 255)  # White text
    
    # Draw rectangle
    cv2.rectangle(img, (left, top), (right, bottom), rect_color, 2)
    
    # Calculate text size and position
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    text_size = cv2.getTextSize(name, font, font_scale, thickness)[0]
    
    # Position text above rectangle with padding
    text_x = left
    text_y = max(top - 10, text_size[1] + 4)  # Ensure text doesn't go above image
    
    # Draw background rectangle for text
    cv2.rectangle(img, 
                 (text_x, text_y - text_size[1] - 4),
                 (text_x + text_size[0], text_y + 4),
                 rect_color, 
                 cv2.FILLED)
    
    # Draw text
    cv2.putText(img, name, 
                (text_x, text_y),
                font, font_scale, text_color, thickness)
    
    return img

def draw_roi(img, roi, is_entry=True):
    """
    Draw ROI rectangle on image
    
    Args:
        img: Input image
        roi: Tuple of (x, y, width, height)
        is_entry: Boolean to determine color
    """
    if roi:
        x, y, w, h = roi
        color = (0, 255, 0) if is_entry else (0, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        
        # Draw ROI label
        text = "Entry Zone" if is_entry else "Exit Zone"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        # Position text above ROI
        cv2.putText(img, text,
                   (x, y - 10),
                   font, font_scale, color, thickness)
    
    return img

def extract_roi(frame, roi):
    """
    Extract ROI from frame
    
    Args:
        frame: Input frame
        roi: Tuple of (x, y, width, height)
    """
    if roi:
        x, y, w, h = roi
        return frame[y:y+h, x:x+w]
    return frame

def draw_status(img, text, position, is_entry=True):
    """
    Draw status text on image
    
    Args:
        img: Input image
        text: Status text to display
        position: Tuple of (x, y) coordinates
        is_entry: Boolean to determine color
    """
    color = (0, 255, 0) if is_entry else (0, 0, 255)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.7
    thickness = 2
    text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
    
    x, y = position
    cv2.rectangle(img,
                 (x, y - text_size[1] - 4),
                 (x + text_size[0], y + 4),
                 color,
                 cv2.FILLED)
    
    cv2.putText(img, text,
                (x, y),
                font, font_scale, (255, 255, 255), thickness)