# Activity_Surveil

**Activity_Surveil** is a Python-based project that enables motion and sound-triggered surveillance recording. It is designed as a practice project for creating a complete system and is not intended for production use. **Please do not take it seriously.**

---

## Features

- **Motion and Sound Detection**: Triggers recording when motion or sound surpasses configurable thresholds.
- **Dual Recording Modes**: Captures both video and audio simultaneously.
- **Configurable Parameters**: Adjustable sensitivity for motion and sound thresholds.
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
   python record.py [-s]
   ```

   - `-s` or `--show`: (Optional) Display the camera feed. Press ESC to exit.

---

## Configuration

You can adjust the following parameters in `record.py` to suit your needs:

### Motion and Sound Detection

- **`motion_threshold`**: Minimum pixel area for motion detection.
- **`sound_threshold`**: RMS amplitude threshold for sound detection.
- **`no_activity_time_limit`**: Time (in seconds) to stop recording if no motion or sound is detected.

### Video Settings

- **`video_fps`**: Frame rate of the video.
- **`resolution`**: Resolution (width, height) for recording.
- **`output_format`**: File format for the recorded video (e.g., `mp4`).

### Audio Settings

- **`CHUNK`**: Number of audio samples per buffer. Adjust this if audio and video are out of sync.
- **`CHANNELS`**: Number of audio channels (e.g., stereo).
- **`RATE`**: Sampling rate for audio recording.

---

## Troubleshooting

- Ensure your camera and microphone are properly connected and accessible.
- Check permissions for creating directories and saving files.
- If FFmpeg is not working, ensure it is installed and added to your system’s PATH.
- If you experience audio-video synchronization problems, try adjusting the value of `CHUNK` in `record.py`.

---
