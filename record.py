import cv2
import numpy as np
import datetime
import os
import platform
import time
import argparse  # For parsing command-line arguments
import pyaudio
import wave
import subprocess

# ==========================
# Adjustable Parameters
# ==========================
motion_threshold = 50000     # Motion detection threshold (pixel area)
sound_threshold = 500        # Sound detection threshold (RMS amplitude)
no_activity_time_limit = 20  # No-activity time threshold (seconds)

# Video recording parameters
video_fps = 10.0             # Video frame rate
resolution = (1280, 720)     # Video resolution, default is 1280x720
output_format = 'mp4'        # Output video format, default MP4
codec_windows = 'mp4v'       # Video codec for Windows
codec_linux = 'mp4v'         # Video codec for Linux

# Audio recording parameters
CHUNK = 1024                 # Number of audio samples per buffer
FORMAT = pyaudio.paInt16     # Audio format (16-bit PCM)
CHANNELS = 2                 # Number of audio channels (stereo)
RATE = 44100                 # Sampling rate (Hz)
# ==========================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Motion and sound detection video recording script.")
    parser.add_argument('-s', '--show', action='store_true', help="Show the camera feed in a window.")
    return parser.parse_args()

def main():
    # Parse command-line arguments
    args = parse_arguments()
    show_window = args.show

    # Determine the platform to select appropriate codec
    system_name = platform.system()
    codec = codec_windows if system_name == "Windows" else codec_linux

    # Get the current directory
    current_path = os.path.dirname(os.path.abspath(__file__))

    # Get current date string in the format YYYYMMDD
    today_str = datetime.datetime.now().strftime('%Y%m%d')

    # Define the path to save videos with a date subfolder
    date_path = os.path.join(current_path, 'videos', today_str)

    # Create the date subfolder if it doesn't exist
    if not os.path.exists(date_path):
        os.makedirs(date_path)

    # Initialize the camera (default camera index 0)
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened successfully
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
    last_activity_time = None  # Time of last detected motion or sound
    recording = False  # Is recording ongoing
    out = None
    audio_frames = []

    # Initialize PyAudio
    p = pyaudio.PyAudio()

    # Open audio stream
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    try:
        while cap.isOpened():
            # Read audio data
            data = stream.read(CHUNK, exception_on_overflow=False)
            data_int = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(data_int ** 2))
            sound_detected = rms > sound_threshold

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

            if motion or sound_detected:
                last_activity_time = current_time  # Update the last activity detection time
                if not recording:
                    # Start recording
                    recording = True
                    start_time = datetime.datetime.now()
                    start_time_str = start_time.strftime("%Y%m%d_%H%M%S")
                    # Define video save path and filename, save to date subfolder
                    video_filename = os.path.join(date_path, f"{start_time_str}_video_temp.{output_format}")
                    out = cv2.VideoWriter(video_filename, fourcc, video_fps, resolution)
                    print(f"Recording started: {video_filename}")
                    # Initialize audio frames
                    audio_frames = []

            if recording:
                out.write(frame1)  # Write the video frame
                # Append audio data to audio_frames
                audio_frames.append(data)
                # Check if the no-activity time threshold has been exceeded
                if last_activity_time and (current_time - last_activity_time > no_activity_time_limit):
                    # Stop recording
                    recording = False
                    out.release()
                    out = None
                    end_time = datetime.datetime.now()
                    end_time_str = end_time.strftime("%Y%m%d_%H%M%S")

                    # Save audio data to .wav file
                    audio_filename = os.path.join(date_path, f"{start_time_str}_audio_temp.wav")
                    wf = wave.open(audio_filename, 'wb')
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(p.get_sample_size(FORMAT))
                    wf.setframerate(RATE)
                    wf.writeframes(b''.join(audio_frames))
                    wf.close()

                    # Combine audio and video using FFmpeg
                    final_filename = os.path.join(date_path, f"{start_time_str}_{end_time_str}.{output_format}")
                    ffmpeg_command = [
                        'ffmpeg',
                        '-y',
                        '-i', video_filename,
                        '-i', audio_filename,
                        '-c:v', 'copy',
                        '-c:a', 'aac',
                        '-strict', 'experimental',
                        final_filename
                    ]
                    subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

                    # Remove temporary files
                    os.remove(video_filename)
                    os.remove(audio_filename)
                    print(f"Recording saved: {final_filename}")

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

        # End of while loop

    except KeyboardInterrupt:
        print("Program interrupted. Cleaning up resources...")

    finally:
        # Ensure proper release of resources
        if recording:
            if out is not None:
                out.release()
                print("Stopped recording and released video writer.")
            if audio_frames:
                # Save any remaining audio data
                end_time = datetime.datetime.now()
                end_time_str = end_time.strftime("%Y%m%d_%H%M%S")
                # Save audio data to .wav file
                audio_filename = os.path.join(date_path, f"{start_time_str}_audio_temp.wav")
                wf = wave.open(audio_filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(audio_frames))
                wf.close()

                # Combine audio and video using FFmpeg
                final_filename = os.path.join(date_path, f"{start_time_str}_{end_time_str}.{output_format}")
                ffmpeg_command = [
                    'ffmpeg',
                    '-y',
                    '-i', video_filename,
                    '-i', audio_filename,
                    '-c:v', 'copy',
                    '-c:a', 'aac',
                    '-strict', 'experimental',
                    final_filename
                ]
                subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

                # Remove temporary files
                os.remove(video_filename)
                os.remove(audio_filename)
                print(f"Recording saved: {final_filename}")

        # Close audio stream and terminate PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()
        cap.release()
        cv2.destroyAllWindows()
        print("Released camera and destroyed all windows.")

if __name__ == "__main__":
    main()
