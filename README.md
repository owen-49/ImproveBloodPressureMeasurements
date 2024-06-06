# Improve Blood Pressure Measurements

This project aims to improve the accuracy of blood pressure measurements using video-based heart rate monitoring and a calculation algorithm. The system utilizes facial tracking to detect and analyze heart rate data, which is then used to estimate blood pressure.

## Features

- **Real-time heart rate monitoring** using facial recognition and video processing.
- **Blood pressure calculation** based on heart rate, weight, height, and age.
- **Graphical display** of heart rate data and trends using PyQt5.

## Project Structure

- **blood_pressure_calculator.py**: Contains the algorithm to calculate blood pressure based on heart rate and other personal parameters.
- **conf.py**: Configuration file with settings for the heart rate monitoring system.
- **facetracker.py**: Handles face detection and tracking using OpenCV.
- **person.py**: Manages individual user data and processes heart rate signals.
- **plot.py**: Utilizes PyQt5 to display graphical representations of heart rate data.
- **main.py**: Entry point for running the heart rate monitoring and blood pressure calculation system.
- **pulse.py**: Main application logic for the heart rate monitoring system.
- **sceneanalyzer.py**: Analyzes heart rate for persons in a video frame.
- **util.py**: Utility functions for the application.
- **videostream.py**: Handles the video stream from the webcam.
- **widgets.py**: GUI components for displaying video and graphs.

## Setup

1. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure settings:**
You can adjust the settings in `conf.py` or override them by creating a `.heartwave.conf` file in your home directory with your custom settings.

## Usage

To run the system, execute the main script:

```bash
python main.py
```
This will start the heart rate monitoring system, which uses your computer's webcam to detect and track faces, analyze heart rate data, and estimate blood pressure.
  
## Detailed Description of Key Components
`blood_pressure_calculator.py`
This module calculates systolic and diastolic blood pressure using the following formula:
```python
def blood_pressure_calculator(avg_bpm, weight, height, age):
    kgs = weight * 0.45359237  # lbs to kgs
    cm = height / 0.39370  # in to cm
    Q = 4.5  # constant

    rob = 18.5
    et = (364.5 - 1.23 * avg_bpm)
    bsa = 0.007184 * (kgs ** 0.425) * (cm ** 0.725)
    sv = (-6.6 + (0.25 * (et - 35)) - (0.62 * avg_bpm) + (40.4 * bsa) - (0.51 * age))
    pp = sv / ((0.013 * kgs - 0.007 * age - 0.004 * avg_bpm) + 1.307)
    mpp = Q * rob

    sp = int(mpp + 3 / 2 * pp)
    dp = int(mpp - pp / 3)

    return sp, dp
```

`facetracker.py`
This module uses OpenCV to detect and track faces in the video feed. It processes frames to identify regions of interest (ROI) for heart rate analysis.

`person.py`
The Person class manages individual user's heart rate data, including raw signal processing, bandpass filtering, and frequency spectrum analysis.

`plot.py`
This module provides functionalities to plot heart rate data using PyQt5. It can display real-time heart rate trends and other related information.

`conf.py`
This configuration file includes settings such as minimum and maximum heart rate, camera ID, sampling periods, and timeouts. Users can override these settings by creating a .heartwave.conf file in their home directory.

`pulse.py`
This module contains the main application logic for starting the heart rate monitoring system. It initializes the video stream, face tracker, and scene analyzer, and displays the results in a GUI.

`sceneanalyzer.py`
This module analyzes heart rate for persons in a scene by processing frames and identifying heart rate data from detected faces.

`util.py`
Utility functions used across the application, including functions for running the event loop and converting images.

`videostream.py`
Handles the video stream from the webcam, emitting frames to be processed by other modules.

`widgets.py`
GUI components for displaying video and graphical plots of heart rate data.
   