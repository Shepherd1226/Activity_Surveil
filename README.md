# Activity_Surveil

**Activity_Surveil** is a Python-based project that enables motion and sound-triggered surveillance recording. It is designed as a practice project for creating a complete system and is not intended for production use. **Please do not take it seriously.**

---

## Features

- **Multiple Detection Modes**: Triggers recording when motion, sound, or either surpass thresholds.
- **Multiple Recording Modes**: Captures video, audio, or both simultaneously.
- **Configurable Parameters**: Adjustable sensitivity for motion and sound thresholds.
- **Real-time Threshold Monitoring**: Provides debug mode displaying real-time sound and motion measurements for easy threshold adjustment.
- **Hardware Capability Measuring**: Measure camera and microphone capabilities to help choose appropriate parameters.
- **Platform Compatibility**: Works on Windows, Linux, and macOS platforms.

---

## Requirements

Set up the environment using the included `environment.yml` file.

1. Install Conda if you haven’t already.
2. Create a Conda environment:

   ```bash
   conda env create -f environment.yml
   ```

3. Activate the environment:

   ```bash
   conda activate Surveillance
   ```

---

## Usage

### Testing Camera and Audio Capabilities

1. Run `measure.py` to test the camera's resolution, frame rate, and audio device capabilities:

   ```bash
   python measure.py
   ```

### Activity Detection and Recording

1. Run `record.py` to start motion and sound-triggered recording:

   ```bash
   python record.py [-s] [-d]
   ```

   - `-s` or `--show`: (Optional) Display the camera feed. Press ESC to exit.
   - `-d` or `--debug`: (Optional) Enable debug mode with detailed output.

---

## Configuration

You can adjust the following parameters in `record.py` to suit your needs:

### Motion and Sound Detection

- **`motion_threshold`**: Minimum pixel area for motion detection.
- **`sound_threshold`**: RMS amplitude threshold for sound detection.
- **`no_activity_time_limit`**: Time (in seconds) to stop recording if no motion or sound is detected.
- **`trigger_method`**: Method to trigger recording: 'motion', 'sound', or 'either'.
- **`record_content`**: Content to record: 'video', 'audio', 'both', or 'none'.

### Video Settings

- **`video_fps`**: Frame rate of the video.
- **`resolution`**: Resolution (width, height) for recording.
- **`output_format`**: File format for the recorded video (e.g., `mp4`).

### Audio Settings

- **`chunk`**: Number of audio samples per buffer.
- **`channels`**: Number of audio channels (e.g., stereo).
- **`rate`**: Sampling rate for audio recording.

---

## Troubleshooting

- **Camera and Microphone Connection:** Ensure your camera and microphone are properly connected and accessible. Note that using WSL (Windows Subsystem for Linux) or a virtual machine may prevent proper connection to the camera.
  
- **Audio-Video Synchronization:** If you experience audio-video synchronization problems, try adjusting the value of `chunk` in `record.py`. Smaller chunks mean higher frequency function calls, which might conflict with the video recording process.

- **Permissions Issues:** Check permissions for creating directories and saving files.

- **FFmpeg Installation:** If FFmpeg is not working, ensure it is installed and added to your system’s PATH.

---