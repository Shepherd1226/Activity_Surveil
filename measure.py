import cv2
import platform
import pyaudio

# ==========================
# Test Maximum Resolution, Frame Rate, and Audio Capabilities
# ==========================

def detect_cameras():
    """Detect available camera devices."""
    print("Detecting available camera devices...")
    index = 0
    available_cameras = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            break
        else:
            available_cameras.append(index)
        cap.release()
        index += 1

    if available_cameras:
        print(f"Available camera devices: {available_cameras}")
    else:
        print("No camera devices detected.")
    return available_cameras

def measure_camera():
    """Query the maximum resolution and frame rate supported by the camera."""
    available_cameras = detect_cameras()
    if not available_cameras:
        print("Error: No cameras to measure.")
        return

    for cam_index in available_cameras:
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
            print(f"Error: Unable to access camera {cam_index}.")
            continue

        print(f"Querying the maximum resolution and frame rate for camera {cam_index}...")

        try:
            # Attempt to set ultra-high resolution and frame rate to test hardware limits
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 9999)  # Try a large width
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 9999)  # Try a large height
            cap.set(cv2.CAP_PROP_FPS, 180)  # Try a high frame rate

            # Get the actual resolution and frame rate after setting
            max_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            max_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            max_fps = int(cap.get(cv2.CAP_PROP_FPS))

            print(f"Camera {cam_index}: Maximum resolution supported: {max_width}x{max_height}")
            print(f"Camera {cam_index}: Maximum frame rate supported: {max_fps}")

        except Exception as e:
            print(f"An error occurred while measuring camera {cam_index}: {e}")

        finally:
            cap.release()
            print(f"Camera {cam_index} resources released.")

def measure_audio():
    """Query the audio device capabilities."""
    p = pyaudio.PyAudio()

    print("Querying audio input device capabilities...")
    try:
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Audio Device {i}: {device_info['name']}")
                print(f" - Max Input Channels: {device_info['maxInputChannels']}")
                print(f" - Default Sample Rate: {device_info['defaultSampleRate']} Hz")
                print(f" - Default Low Input Latency: {device_info['defaultLowInputLatency']} s")
                print(f" - Default High Input Latency: {device_info['defaultHighInputLatency']} s")
    except Exception as e:
        print(f"An error occurred while measuring audio: {e}")
    finally:
        p.terminate()
        print("Audio resources released.")

def main():
    system_name = platform.system()
    print(f"Operating System: {system_name}")
    measure_camera()
    measure_audio()

if __name__ == "__main__":
    main()
