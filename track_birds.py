import cv2
import numpy as np
import os

# Load video
video_path = 'input.mp4'
print(os.listdir())
if not os.path.exists(video_path):
    print(f"Error: Video file '{video_path}' does not exist.")
    exit()

cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)  # Explicit FFMPEG backend

# Check if video opened
if not cap.isOpened():
    print("Error: Could not open input video. Check file format or OpenCV FFMPEG support.")
    print(f"File path: {os.path.abspath(video_path)}")
    exit()

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"Video loaded: {width}x{height}, {fps} FPS, {total_frames} frames")

# Output video setup
output_path = 'output_video.avi'
fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # MJPG for Windows compatibility
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height), isColor=True)

# Check if writer is opened
if not out.isOpened():
    print("Error: Could not open output video writer.")
    cap.release()
    exit()

# Parameters for bird detection
min_area = 50  # Minimum area of detected birds
max_area = 500  # Maximum area to avoid large objects

# Initialize trackers (CSRT for accuracy)
trackers = []
max_trackers = 3  # Track up to 3 birds

def create_tracker():
    return cv2.TrackerCSRT_create()

# Process frames
frame_count = 0
birds_detected = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    print(f'Processing frame {frame_count}/{total_frames}')

    # Convert to grayscale and apply background subtraction
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize trackers for detected birds
    if not birds_detected and len(trackers) < max_trackers:
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                (x, y, w, h) = cv2.boundingRect(contour)
                tracker = create_tracker()
                try:
                    tracker.init(frame, (x, y, w, h))
                    trackers.append(tracker)
                    if len(trackers) >= max_trackers:
                        birds_detected = True
                        break
                except Exception as e:
                    print(f"Warning: Tracker init failed: {e}")

    # Update trackers and draw circles
    for tracker in trackers:
        success, box = tracker.update(frame)
        if success:
            (x, y, w, h) = [int(v) for v in box]
            center = (x + w // 2, y + h // 2)
            radius = max(w, h) // 2 + 5
            cv2.circle(frame, center, radius, (0, 255, 0), 2)

    # Write frame to output
    out.write(frame)

# Release resources
cap.release()
out.release()
cv2.destroyAllWindows()
print(f'Output saved to {output_path}')