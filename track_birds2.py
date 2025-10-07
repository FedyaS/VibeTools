import cv2
import numpy as np
import torch
from torchvision import transforms
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from sort import Sort
from tqdm import tqdm

# Set up device (GPU if available, else CPU)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Load the pre-trained Faster R-CNN model and move to device
model = fasterrcnn_resnet50_fpn(pretrained=True).to(device)
model.eval()

# Initialize the SORT tracker
tracker = Sort()

# Define the transformation to convert frame to tensor
transform = transforms.Compose([transforms.ToTensor()])

# Open the input video
cap = cv2.VideoCapture('input.mp4')
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Set up the output video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

# Initialize progress bar
pbar = tqdm(total=total_frames, desc="Processing frames")

# Process each frame
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to tensor and move to device
    frame_tensor = transform(frame).unsqueeze(0).to(device)

    # Run the model to get detections
    with torch.no_grad():
        predictions = model(frame_tensor)

    # Extract boxes, labels, and scores
    boxes = predictions[0]['boxes'].cpu().numpy()
    labels = predictions[0]['labels'].cpu().numpy()
    scores = predictions[0]['scores'].cpu().numpy()

    # Filter detections for birds (COCO class 16) with confidence > 0.5
    bird_indices = np.where((labels == 16) & (scores > 0.2))[0]
    detections = boxes[bird_indices]
    det_scores = scores[bird_indices]

    # Prepare detections for tracker: [x1, y1, x2, y2, score]
    if len(detections) > 0:
        detections_for_tracker = np.hstack((detections, det_scores.reshape(-1, 1)))
    else:
        detections_for_tracker = np.empty((0, 5))

    # Update the tracker with detections
    tracked_objects = tracker.update(detections_for_tracker)

    # Draw orange circles for each tracked bird
    for obj in tracked_objects:
        x1, y1, x2, y2, track_id = obj
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        w = x2 - x1
        h = y2 - y1
        radius = np.sqrt((w / 2) ** 2 + (h / 2) ** 2)
        cv2.circle(frame, (int(center_x), int(center_y)), int(radius), (0, 165, 255), 2)

    # Write the annotated frame to the output video
    out.write(frame)

    # Update the progress bar
    pbar.update(1)

# Close the progress bar and release resources
pbar.close()
cap.release()
out.release()