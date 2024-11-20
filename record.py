import cv2
import numpy as np
import datetime
import os
import platform
import time
import argparse  # For parsing command-line arguments

# ==========================
# Adjustable Parameters
# ==========================
motion_threshold = 100  # Motion detection threshold (pixel area)
no_motion_time_limit = 10  # No-motion time threshold (seconds)
video_fps = 20.0  # Video frame rate
resolution = (1280, 720)  # Video resolution, default 640x480
output_format = 'mp4'  # Output video format, default MP4
codec_windows = 'mp4v'  # Video codec for Windows (compatible with MP4 format)
codec_linux = 'mp4v'  # Video codec for Linux
# ==========================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Motion detection video recording script.")
    parser.add_argument('-s', '--show', action='store_true', help="Show the camera feed in a window.")
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()
    show_window = args.show

    # Determine the platform
    system_name = platform.system()
    codec = codec_windows if system_name == "Windows" else codec_linux

    # Record current directory
    current_path = os.path.dirname(os.path.abspath(__file__))

    # Get current date string in the format YYYYMMDD
    today_str = datetime.datetime.now().strftime('%Y%m%d')

    # Define the path to save videos with a date subfolder
    date_path = os.path.join(current_path, 'videos', today_str)

    # Create the date subfolder if it doesn't exist
    if not os.path.exists(date_path):
        os.makedirs(date_path)

    # Reinitialize the camera
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    # Define the video codec format
    fourcc = cv2.VideoWriter_fourcc(*codec)

    # Initialize variables
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    motion_detected = False
    last_motion_time = None  # Time of last detected motion
    recording = False  # Is recording ongoing
    out = None

    try:
        while cap.isOpened():
            # Calculate the difference between two frames
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Detect motion
            motion = False
            for contour in contours:
                if cv2.contourArea(contour) < motion_threshold:
                    continue
                motion = True
                break

            current_time = time.time()

            if motion:
                last_motion_time = current_time  # Update the last motion detection time
                if not recording:
                    # Start recording
                    recording = True
                    start_time = datetime.datetime.now()
                    start_time_str = start_time.strftime("%Y%m%d_%H%M%S")
                    # Define video save path and filename, save to date subfolder
                    video_filename = os.path.join(date_path, f"{start_time_str}.{output_format}")
                    out = cv2.VideoWriter(video_filename, fourcc, video_fps, resolution)
                    print(f"Recording started: {video_filename}")

            if recording:
                out.write(frame1)  # Write the video frame
                # Check if the no-motion time threshold has been exceeded
                if last_motion_time and (current_time - last_motion_time > no_motion_time_limit):
                    # Stop recording
                    recording = False
                    out.release()
                    out = None
                    end_time = datetime.datetime.now()
                    end_time_str = end_time.strftime("%Y%m%d_%H%M%S")
                    new_video_filename = os.path.join(date_path, f"{start_time_str}_{end_time_str}.{output_format}")
                    os.rename(video_filename, new_video_filename)
                    print(f"Recording saved: {new_video_filename}")

            # Optional: Display video feed
            if show_window:
                cv2.imshow('Camera', frame1)
                if cv2.waitKey(1) == 27:  # Press ESC to exit
                    break

            # Update frames
            frame1 = frame2
            ret, frame2 = cap.read()
            if not ret:
                break

    except KeyboardInterrupt:
        print("Program interrupted. Cleaning up resources...")

    finally:
        # Ensure proper release of resources
        if recording and out is not None:
            out.release()
            print("Stopped recording and released video writer.")
        cap.release()
        cv2.destroyAllWindows()
        print("Released camera and destroyed all windows.")

if __name__ == "__main__":
    main()
