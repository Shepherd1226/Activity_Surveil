# Motion Surveil

**Motion Surveil** is a Python-based project that automatically enables surveillance footage recording when motion is detected. It is designed for applications such as home security, wildlife monitoring, or general motion-triggered recording systems.

---

## Features

- **Automatic Motion Detection**: Records video when motion is detected.
- **Configurable Thresholds**: Adjustable parameters for motion sensitivity and recording behavior.
- **High-Resolution Support**: Supports testing and setting maximum camera resolution and frame rates.
- **Platform Compatibility**: Works on Windows and Linux platforms.
- **Video Management**: Saves video recordings in a structured date-based folder system.
- **Record Videos Using Your Computer Camera**: Utilize your computer's camera for testing and recording purposes.

---

## Requirements

Ensure you have the following dependencies installed. The project includes a `requirements.txt` for easy setup.

- Python 3.7+
- OpenCV (`cv2`)
- NumPy
- argparse

To install dependencies, run:

```bash
pip install -r requirements.txt
```

---

## Usage

### Running the Program

1. **Testing Camera Capabilities**:
   Use `measure.py` to test the maximum resolution and frame rate supported by your camera.

   ```bash
   python measure.py
   ```

2. **Motion Detection and Recording**:
   Use `record.py` to enable motion-triggered video recording.

   ```bash
   python record.py [-s]
   ```

   - `-s` or `--show`: (Optional) Show the camera feed in a window. You can press ESC to exit.

---

## Configuration

You can configure the following parameters directly in the `record.py` script:

- `motion_threshold`: Minimum motion area (in pixels) to trigger recording.
- `no_motion_time_limit`: Time (in seconds) after which recording stops if no motion is detected.
- `video_fps`: Frame rate for the recorded video.
- `resolution`: Camera resolution (width, height) for recording.
- `output_format`: File format for saving videos (e.g., `mp4`).
- `codec_windows` and `codec_linux`: Codec used for encoding videos depending on the platform.

---

## How It Works

1. **Motion Detection**:
   - Detects motion using frame differencing, grayscale conversion, Gaussian blurring, and contour detection.
   - Starts recording when motion surpasses the defined threshold.

2. **Recording Management**:
   - Saves recordings in a folder structure based on the current date.
   - Stops recording if no motion is detected for the specified time limit.

3. **Camera Capability Testing**:
   - `measure.py` attempts to query and display the camera's maximum resolution and frame rate.

---

## File Structure

- `measure.py`: Tests and displays maximum camera resolution and frame rates.
- `record.py`: Main script for motion detection and recording.
- `requirements.txt`: List of Python dependencies for the project.

---

## Output

Recorded videos are saved in the `videos` directory within subfolders named by the current date (e.g., `videos/20241120/`).

---

## Notes

- This project is **just a test** of the process of creating a complete project. **Please do not take it seriously.**
- The recordings and functionality provided are for experimental purposes and should not be used as a finalized solution for surveillance needs.

---

## Contributions

Contributions are welcome! Feel free to fork the repository and submit pull requests.

---

## Troubleshooting

- Ensure your camera is connected and accessible by OpenCV.
- Check permissions for creating directories and saving files.
- If `cv2.VideoWriter` fails, ensure you have the proper codec installed on your system.

---

## Contact

For questions or issues, please contact the project maintainer.

--- 
