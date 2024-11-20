import cv2
import platform

# ==========================
# Test Maximum Resolution and Frame Rate Supported by Hardware
# ==========================

def main():
    # Check the operating system
    system_name = platform.system()

    # Initialize camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the camera.")
        return

    print("Querying the maximum resolution and frame rate supported by the camera...")

    try:
        # Attempt to set ultra-high resolution and frame rate to test hardware limits
        if system_name == "Windows":
            # Windows system may handle these directly
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 9999)  # Attempt ultra-high width
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 9999)  # Attempt ultra-high height
            cap.set(cv2.CAP_PROP_FPS, 200)  # Attempt ultra-high frame rate
        elif system_name == "Linux":
            # Ubuntu/Linux systems may require more realistic limits
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)  # Common max width for modern cameras
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)  # Common max height for modern cameras
            cap.set(cv2.CAP_PROP_FPS, 120)  # Common high frame rate

        # Get the actual resolution and frame rate after setting
        max_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        max_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        max_fps = int(cap.get(cv2.CAP_PROP_FPS))

        print(f"Maximum resolution supported by the camera: {max_width}x{max_height}")
        print(f"Maximum frame rate supported by the camera: {max_fps}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Release camera resources
        print("Releasing camera resources...")
        cap.release()
        print("Camera resources released.")

if __name__ == "__main__":
    main()
