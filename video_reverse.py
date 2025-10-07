import cv2
import tqdm


def reverse_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    frames = []
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for _ in tqdm.trange(total_frames, desc="Reading frames"):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()

    height, width = frames[0].shape[:2]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, 30.0, (width, height))

    for frame in tqdm.tqdm(reversed(frames), total=len(frames), desc="Writing frames"):
        out.write(frame)
    out.release()


if __name__ == "__main__":
    reverse_video("reverse_me.MP4", "output_reversed.mp4")