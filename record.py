import cv2
import numpy as np
import datetime
import os
import platform
import time
import argparse
import pyaudio
import wave
import subprocess

# ==========================
# Adjustable Parameters
# ==========================
motion_threshold = 30000     # Motion detection threshold (pixel area)
sound_threshold = 85         # Sound detection threshold (RMS amplitude)
no_activity_time_limit = 10  # No-activity time threshold (seconds)
trigger_method = 'either'    # Trigger method: 'motion', 'sound', or 'either'
record_content = 'both'      # Record content: 'video', 'audio', or 'both'

# Video recording parameters
video_fps = 10.0             # Video frame rate
resolution = (1280, 720)     # Video resolution, default is 1280x720
output_format = 'mp4'        # Output video format, default MP4
codec_windows = 'mp4v'       # Video codec for Windows
codec_linux = 'mp4v'         # Video codec for Linux
codec_mac = 'avc1'           # Video codec for macOS

# Audio recording parameters
CHUNK = 4096                 # Number of audio samples per buffer
FORMAT = pyaudio.paInt16     # Audio format (16-bit PCM)
CHANNELS = 2                 # Number of audio channels (stereo)
RATE = 44100                 # Sampling rate (Hz)
# ==========================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Motion and sound detection video recording script.")
    parser.add_argument('-s', '--show', action='store_true', help="Show the camera feed in a window.")
    return parser.parse_args()

def get_codec():
    """Determine the appropriate video codec based on the operating system."""
    system_name = platform.system()
    if system_name == "Windows":
        return codec_windows
    elif system_name == "Linux":
        return codec_linux
    elif system_name == "Darwin": 
        return codec_mac
    else:
        print("Unsupported platform:", system_name)
        return None

def setup_paths():
    """Set up the directory paths for saving videos."""
    current_path = os.path.dirname(os.path.abspath(__file__))
    today_str = datetime.datetime.now().strftime('%Y%m%d')
    date_path = os.path.join(current_path, 'videos', today_str)
    if not os.path.exists(date_path):
        os.makedirs(date_path)
    return date_path

def initialize_camera():
    """Initialize the camera and set the resolution."""
    cap = cv2.VideoCapture(0) # Run measure.py to check the camera index
    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    return cap

def initialize_audio():
    """Initialize PyAudio and open the audio stream."""
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    return p, stream

def detect_sound(stream):
    """Read audio data from the stream and detect sound based on RMS amplitude."""
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data_int = np.frombuffer(data, dtype=np.int16)
        if len(data_int) == 0 or (not np.any(data_int)):
            return False, data
        mse = np.mean(data_int ** 2)
        if not mse or mse<0:
            return False, data
        rms = np.sqrt(mse)
        return rms > sound_threshold, data
    except Exception as e:
        print("Audio capture error:", e)
        return False, b''

def detect_motion(frame1, frame2):
    """Detect motion between two consecutive frames."""
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) >= motion_threshold:
            return True
    return False

def start_recording(codec, date_path):
    """Start recording by initializing VideoWriter and resetting audio frames."""
    start_time = datetime.datetime.now()
    start_time_str = start_time.strftime("%Y%m%d_%H%M%S")
    video_filename = os.path.join(date_path, f"{start_time_str}_video_temp.{output_format}")
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(video_filename, fourcc, video_fps, resolution)
    print(f"Recording started: {start_time_str}")
    audio_frames = []
    return out, start_time_str, audio_frames

def stop_recording(out, audio_frames, start_time_str, date_path, p):
    """Stop recording, save audio, combine audio and video, and clean up temporary files."""
    out.release()
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
    
    if record_content == 'both':
        # Combine audio and video using FFmpeg
        final_filename = os.path.join(date_path, f"{start_time_str}_{end_time_str}.{output_format}")
        ffmpeg_command = [
            'ffmpeg',
            '-y',
            '-i', os.path.join(date_path, f"{start_time_str}_video_temp.{output_format}"),
            '-i', audio_filename,
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-strict', 'experimental',
            final_filename
        ]
        subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
        
        # Remove temporary files
        os.remove(os.path.join(date_path, f"{start_time_str}_video_temp.{output_format}"))
        os.remove(audio_filename)
    elif record_content == 'video':
        final_filename = os.path.join(date_path, f"{start_time_str}_{end_time_str}.{output_format}")
        os.rename(os.path.join(date_path, f"{start_time_str}_video_temp.{output_format}"), final_filename)
        os.remove(audio_filename)
    elif record_content == 'audio':
        final_filename = os.path.join(date_path, f"{start_time_str}_{end_time_str}.wav")
        os.rename(audio_filename, final_filename)
        os.remove(os.path.join(date_path, f"{start_time_str}_video_temp.{output_format}"))

    return final_filename, end_time_str

def display_frame(show_window, frame):
    """Display the current video frame if the show_window flag is True."""
    if show_window:
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) == 27:  # Press ESC to exit
            return False
    return True

def cleanup(recording, out, audio_frames, start_time_str, date_path, p, stream, cap):
    """Release all resources and handle any remaining recordings."""
    if recording:
        final_filename, end_time_str = stop_recording(out, audio_frames, start_time_str, date_path, p)
        print(f"Recording stopped: {end_time_str}")
    
    # Close audio stream and terminate PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()
    cap.release()
    cv2.destroyAllWindows()
    print("All cleaned.")

def main():
    # Parse command-line arguments
    args = parse_arguments()
    show_window = args.show

    # Determine the platform to select appropriate codec
    codec = get_codec()
    if codec is None:
        return
    fourcc = cv2.VideoWriter_fourcc(*codec)

    # Set up paths for saving videos
    date_path = setup_paths()

    # Initialize the camera
    cap = initialize_camera()
    if cap is None:
        return
    
    # Initialize audio
    p, stream = initialize_audio()

    # Initialize frames for motion detection
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    if not ret:
        print("Error: Unable to read frames from the camera.")
        cap.release()
        return

    last_activity_time = None  # Time of last detected motion or sound
    recording = False  # Is recording ongoing
    audio_frames = []  # Audio data buffer
    out = None  # Video writer object
    start_time_str = ""  # Start time string
    print("Initialized successfully.")

    try:
        while cap.isOpened():
            # Detect activity based on motion and sound
            sound_detected, data = detect_sound(stream)
            motion = detect_motion(frame1, frame2)
            sound_detected = sound_detected and (trigger_method in ['sound', 'either'])
            motion = motion and (trigger_method in ['motion', 'either'])
            current_time = time.time()

            if motion or sound_detected:
                last_activity_time = current_time  # Update the last activity detection time
                if not recording:
                    # Start recording
                    out, start_time_str, audio_frames = start_recording(codec, date_path)
                    recording = True

            if recording:
                out.write(frame1)  # Write the video frame
                audio_frames.append(data)  # Append audio data
                # Check if the no-activity time threshold has been exceeded
                if last_activity_time and (current_time - last_activity_time > no_activity_time_limit):
                    # Stop recording
                    final_filename, end_time_str = stop_recording(out, audio_frames, start_time_str, date_path, p)
                    print(f"Recording stopped: {end_time_str}")
                    recording = False
            else:
                print("Standing by...", end="\r")

            # Optional: Display video feed
            continue_running = display_frame(show_window, frame1)
            if not continue_running:
                break

            # Update frames for the next iteration
            frame1 = frame2
            ret, frame2 = cap.read()
            if not ret:
                break

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Cleaning up resources...")

    finally:
        # Handle cleanup and ensure all resources are released
        cleanup(recording, out, audio_frames, start_time_str, date_path, p, stream, cap)

if __name__ == "__main__":
    main()