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
sound_threshold = 500        # Sound detection threshold (RMS amplitude)
no_activity_time_limit = 10  # No-activity time threshold (seconds)
trigger_method = 'either'    # Trigger method: 'motion', 'sound', or 'either'
record_content = 'both'      # Record content: 'video', 'audio', 'both' or 'none'

# Video recording parameters
video_fps = 10.0             # Video frame rate
resolution = (1280, 720)     # Video resolution, default is 1280x720
output_format = 'mp4'        # Output video format, default MP4
codec_windows = 'mp4v'       # Video codec for Windows
codec_linux = 'mp4v'         # Video codec for Linux
codec_mac = 'avc1'           # Video codec for macOS
camera_index = 0             # Index of the camera to use, run measure.py to check

# Audio recording parameters
chunk = 4096                 # Number of audio samples per buffer
format = pyaudio.paInt16     # Audio format (16-bit PCM)
channels = 2                 # Number of audio channels (stereo)
rate = 44100                 # Sampling rate (Hz)
microphone_index = 0         # Index of the microphone to use, run measure.py to check
# ==========================

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Activity surveillance script.")
    parser.add_argument('-s', '--show', action='store_true', help="Show the camera feed in a window.")
    parser.add_argument('-d', '--debug', action='store_true', help="Enable debug mode with detailed output.")
    return parser.parse_args()

def print_debug_info(system_name, codec, camera_name, microphone_name):
    """Print detailed debug information."""
    print("Debug Mode Enabled")
    print("Platform Information:")
    print(f"{'Platform':<25} {system_name}")
    print(f"{'Codec':<25} {codec}")
    print("\nAdjustable Parameters:")
    print(f"{'Parameter':<25} {'Value'}")
    print(f"{'-'*25} {'-'*25}")
    print(f"{'motion_threshold':<25} {motion_threshold}")
    print(f"{'sound_threshold':<25} {sound_threshold}")
    print(f"{'no_activity_time_limit':<25} {no_activity_time_limit}")
    print(f"{'trigger_method':<25} {trigger_method}")
    print(f"{'record_content':<25} {record_content}")
    print(f"{'-'*25} {'-'*25}")
    print(f"{'video_fps':<25} {video_fps}")
    print(f"{'resolution':<25} {resolution}")
    print(f"{'output_format':<25} {output_format}")
    print(f"{'camera_backend_name':<25} {camera_name}")
    print(f"{'-'*25} {'-'*25}")
    print(f"{'chunk':<25} {chunk}")
    print(f"{'format':<25} {format}")
    print(f"{'channels':<25} {channels}")
    print(f"{'rate':<25} {rate}")
    print(f"{'microphone_name':<25} {microphone_name}")
    print(f"{'-'*25} {'-'*25}")

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
    temp_path = os.path.join(current_path, 'recordings', 'temp')
    recordings_path = os.path.join(current_path, 'recordings', today_str)
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    if not os.path.exists(recordings_path):
        os.makedirs(recordings_path)
    return temp_path, recordings_path

def initialize_camera(camera_index=0):
    """Initialize the camera and set the resolution."""
    cap = cv2.VideoCapture(camera_index) # Run measure.py to check the camera index
    if not cap.isOpened():
        print("Error: Unable to access the camera. Check the camera index.")
        return None
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    return cap

def initialize_audio(microphone_index=0):
    """Initialize PyAudio and open the audio stream."""
    p = pyaudio.PyAudio()
    if p.get_device_count() < 1:
        print("Error: No audio devices found.")
        return None, None
    stream = p.open(format=format,
                    channels=channels,
                    rate=rate,
                    input=True,
                    input_device_index=microphone_index,
                    frames_per_buffer=chunk)
    if stream is None:
        print("Error: Unable to open audio stream. Check the microphone index.")
        return p, None
    return p, stream

def detect_sound(stream, debug_mode=False):
    """Read audio data from the stream and detect sound based on RMS amplitude."""
    try:
        data = stream.read(chunk, exception_on_overflow=False)
        data_int = np.frombuffer(data, dtype=np.int16)
        if len(data_int) == 0 or (not np.any(data_int)):
            return False, data, 0
        # Convert to float to prevent integer overflow
        data_float = data_int.astype(np.float32)
        mse = np.mean(data_float ** 2)
        rms = np.sqrt(mse)
        return rms > sound_threshold, data, int(rms)
    except Exception as e:
        print("Audio capture error:", e)
        return False, b'', 0

def detect_motion(frame1, frame2, debug_mode=False):
    """Detect motion between two consecutive frames."""
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= motion_threshold:
            return True, int(area)
        if area > max_area:
            max_area = int(area)
    return False, max_area

def start_recording(codec, temp_path, p, trigger_reason, debug_mode=False):
    """Start recording by initializing VideoWriter and resetting audio frames."""
    start_time = datetime.datetime.now()
    start_time_str = start_time.strftime("%Y%m%d_%H%M%S")
    readable_start_time = start_time.strftime("%b %d, %Y %I:%M:%S %p")
    if debug_mode:
        readable_start_time = datetime.datetime.now().strftime("%b %d, %Y %I:%M:%S %p")
        print(f"Activated: {readable_start_time}, by {trigger_reason}{' '*25}")
    else:
        print(f"Activated: {readable_start_time}{' '*25}")
    
    video_filename = None
    audio_filename = None
    out = None
    wf = None
    
    if record_content in ['video', 'both']:
        video_filename = os.path.join(temp_path, f"{start_time_str}_video_temp.{output_format}")
        fourcc = cv2.VideoWriter_fourcc(*codec)
        out = cv2.VideoWriter(video_filename, fourcc, video_fps, resolution)
    
    if record_content in ['audio', 'both']:
        audio_filename = os.path.join(temp_path, f"{start_time_str}_audio_temp.wav")
        wf = wave.open(audio_filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
    
    return out, start_time_str, wf, video_filename, audio_filename

def stop_recording(out, wf, start_time_str, recordings_path, p, video_filename, audio_filename, debug_mode=False):
    """Stop recording, save audio, combine audio and video, and clean up temporary files."""
    if out:
        out.release()
    if wf:
        wf.close()
    
    end_time = datetime.datetime.now()
    end_time_str = end_time.strftime("%Y%m%d_%H%M%S")
    readable_end_time = end_time.strftime("%b %d, %Y %I:%M:%S %p")
    print(f"Terminated: {readable_end_time}{' '*25}")
    
    if record_content == 'both':
        # Combine audio and video using FFmpeg
        final_filename = os.path.join(recordings_path, f"{start_time_str}_{end_time_str}.{output_format}")
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
    elif record_content == 'video':
        final_filename = os.path.join(recordings_path, f"{start_time_str}_{end_time_str}.{output_format}")
        os.rename(video_filename, final_filename)
    elif record_content == 'audio':
        final_filename = os.path.join(recordings_path, f"{start_time_str}_{end_time_str}.wav")
        os.rename(audio_filename, final_filename)
    else: 
        final_filename = None

    return final_filename, end_time_str

def display_frame(show_window, frame):
    """Display the current video frame if the show_window flag is True."""
    if show_window:
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) == 27:  # Press ESC to exit
            return False
    return True

def cleanup(recording, out, wf, start_time_str, recordings_path, p, stream, cap, video_filename, audio_filename):
    """Release all resources and handle any remaining recordings."""
    if recording:
        final_filename, end_time_str = stop_recording(out, wf, start_time_str, recordings_path, p, video_filename, audio_filename)
    
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
    debug_mode = args.debug

    # Determine the platform to select appropriate codec
    system_name = platform.system()
    codec = get_codec()
    if codec is None:
        return
    fourcc = cv2.VideoWriter_fourcc(*codec)

    # Initialize the camera and audio
    cap = initialize_camera(camera_index)
    p, stream = initialize_audio(microphone_index)
    if cap is None or p is None:
        return

    # Get device names
    camera_name = cap.getBackendName() if cap else "Unknown"
    microphone_name = p.get_device_info_by_index(microphone_index).get('name', 'Unknown') if p else "Unknown"

    if debug_mode:
        print_debug_info(system_name, codec, camera_name, microphone_name)

    # Set up paths for saving videos
    temp_path, recordings_path = setup_paths()

    # Initialize frames for motion detection
    ret, frame1 = cap.read()
    ret, frame2 = cap.read()
    if not ret:
        print("Error: Unable to read frames from the camera.")
        cap.release()
        return

    last_activity_time = None  # Time of last detected motion or sound
    recording = False  # Is recording ongoing
    wf = None  # Audio file writer object
    out = None  # Video writer object
    video_filename = ""  # Video file name
    audio_filename = ""  # Audio file name
    start_time_str = ""  # Start time string
    print("Initialized successfully.")

    try:
        while cap.isOpened():
            # Detect activity based on motion and sound
            sound_detected, data, rms = detect_sound(stream, debug_mode)
            motion, motion_area = detect_motion(frame1, frame2, debug_mode)
            sound_detected = sound_detected and (trigger_method in ['sound', 'either'])
            motion = motion and (trigger_method in ['motion', 'either'])
            current_time = time.time()

            if motion or sound_detected:
                last_activity_time = current_time  # Update the last activity detection time
                if not recording:
                    # Start recording
                    trigger_reason = "sound" if sound_detected else "motion"
                    out, start_time_str, wf, video_filename, audio_filename = start_recording(codec, temp_path, p, trigger_reason, debug_mode)
                    recording = True

            if recording:
                if out: out.write(frame1)  # Write the video frame
                if wf: wf.writeframes(data)  # Write audio data to file
                # Check if the no-activity time threshold has been exceeded
                if last_activity_time and (current_time - last_activity_time > no_activity_time_limit):
                    # Stop recording
                    final_filename, end_time_str = stop_recording(out, wf, start_time_str, recordings_path, p, video_filename, audio_filename, debug_mode)
                    recording = False
                if debug_mode:
                    if trigger_method == 'sound':
                        print(f"\rCurrent Sound: {rms}{' '*25}", end="\r")
                    elif trigger_method == 'motion':
                        print(f"\rCurrent Motion: {motion_area}{' '*25}", end="\r")
                    elif trigger_method == 'either':
                        print(f"\rCurrent Sound: {rms}, Current Motion: {motion_area}{' '*25}", end="\r")
            else:
                if debug_mode:
                    print(f"\rCurrent Sound: {rms}, Current Motion: {motion_area}, Standing by...{' '*25}", end="\r")
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
        cleanup(recording, out, wf, start_time_str, recordings_path, p, stream, cap, video_filename, audio_filename)

if __name__ == "__main__":
    main()