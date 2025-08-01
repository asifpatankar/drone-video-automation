
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16674664.svg)](https://doi.org/10.5281/zenodo.16674664)

# drone-video-automation
A robust system for automating drone video streaming based on arming/disarming states. This project integrates MAVSDK for drone telemetry with GStreamer for low-latency video streaming, enabling automatic stream control based on drone operation status.

## Features

- **Automatic Stream Control**: Video streaming starts when drone arms, stops when it disarms
- **MAVSDK Integration**: Real-time monitoring of drone telemetry
- **GStreamer Pipeline**: Hardware-accelerated video encoding on Jetson Nano
- **SSH-based Remote Control**: Secure communication between ground station and drone
- **Robust Error Handling**: Graceful recovery from connection issues


## System Architecture

This system consists of three main components:

1. **Ground Station PC**: Runs the control script (`controller.py`) with MAVSDK
2. **PX4 Flight Controller**: Provides arming/disarming telemetry
3. **Jetson Nano**: Executes the GStreamer pipeline for video streaming

## Prerequisites

### Ground Station Requirements

- Python 3.8+
- MAVSDK Python package
- SSH client


### Jetson Nano Requirements

- JetPack 4.6+ (includes GStreamer with NVIDIA acceleration)
- SSH server
- Network connectivity to ground station


## Installation

### 1. Ground Station Setup

#### Clone the Repository

```bash
git clone https://github.com/asifpatankar/drone-video-automation.git
cd drone-video-automation
```


#### Create Conda Environment

```bash
conda env create -f environment.yml
conda activate drone_stream_env
```


#### Configure SSH Key Authentication

This critical step eliminates password prompts during operation:

1. Generate SSH key pair (if you don't already have one):

```bash
ssh-keygen -t rsa -b 4096
```

Press Enter to accept default locations and skip passphrase if desired.

2. Copy the public key to your Jetson Nano:

```bash
ssh-copy-id username@jetson-ip-address
```

Replace `username` and `jetson-ip-address` with your actual values.

3. Test the connection:

```bash
ssh username@jetson-ip-address
```

You should connect without a password prompt.

### 2. Jetson Nano Setup

#### Create Stream Script

1. Connect to your Jetson Nano:

```bash
ssh username@jetson-ip-address
```

2. Create a directory for the streaming script:

```bash
mkdir -p /media/video-stream
```

3. Create the stream script:

```bash
nano /media/video-stream/stream_script.sh
```

4. Paste the following content:

```bash
#!/bin/bash

log_file="/tmp/stream_script.log"

echo "$(date): Received command: $1" >> $log_file

case $1 in
  start)
    echo "$(date): Starting stream" >> $log_file
    gst-launch-1.0 nvarguscamerasrc ! "video/x-raw(memory:NVMM)",width=1920,height=1080,framerate=30/1,format=NV12 ! videoconvert ! omxh264enc control-rate=constant bitrate=5000000 iframeinterval=15 ! h264parse ! rtph264pay name=pay0 pt=96 config-interval=-1 ! udpsink host=GROUND_STATION_IP port=5600 sync=false &
    echo $! > /tmp/stream_pid
    ;;
  stop)
    echo "$(date): Stopping stream" >> $log_file
    if [ -f /tmp/stream_pid ]; then
      pid = $(cat /tmp/stream_pid)
      kill $pid
      rm /tmp/stream_pid
      echo "$(date): Stopped stream process $pid" >> $log_file
    else
      echo "$(date): No stream process found to stop" >> $log_file
    fi
    ;;
  *)
    echo "$(date): Unknown command" >> $log_file
    ;;
esac
```

Replace `GROUND_STATION_IP` with your ground station's IP address.

5. Make the script executable:

```bash
chmod 755 /media/video-stream/stream_script.sh
```


## Configuration

### Controller Script

Edit the `controller.py` file to match your setup:

```python
# Update these values to match your configuration
JETSON_USER = "username"  # Jetson username
JETSON_IP = "192.168.x.x"  # Jetson IP address
STREAM_SCRIPT = "/media/video-stream/stream_script.sh"
```


## Usage

### 1. Start the Controller

On your ground station:

```bash
conda activate drone_stream_env
python controller.py
```

The script will:

1. Connect to the drone via MAVSDK
2. Monitor the drone's armed state
3. Automatically start/stop video streaming based on arming status

### 2. View the Video Stream

Open QGroundControl and configure the video settings:

1. Open QGroundControl
2. Go to Application Settings (Q icon) > General
3. In the Video section, configure:
    - Video Source: UDP h.264 Video Stream
    - UDP Port: 5600

## Troubleshooting

### Stream Not Starting

1. Check SSH connectivity: `ssh username@jetson-ip-address`
2. Verify script permissions: `ls -l /media/video-stream/stream_script.sh`
3. Check logs on Jetson: `cat /tmp/stream_script.log`

### Video Not Appearing in QGroundControl

1. Ensure ground station and Jetson are on the same network
2. Verify UDP port 5600 is not blocked by firewall
3. Check GStreamer pipeline output for errors

### Frequent Disconnections

1. Improve network stability between ground station and drone
2. Add error handling and reconnection logic to controller script

## Advanced Configuration

### Adjusting Video Quality

Modify the GStreamer pipeline in `stream_script.sh`:

- For lower bandwidth: Reduce resolution (`width=1280,height=720`) and bitrate (`bitrate=2000000`)
- For higher quality: Increase resolution and bitrate, but monitor CPU usage


### Multiple Drones

To manage multiple drones:

1. Assign unique UDP ports for each drone
2. Create separate controller instances with different configuration

## Licensing

This project is available under a dual licensing model:

### Non-Commercial Use
For academic, personal, and non-commercial use, this project is available under the MIT License. See the [LICENSE](LICENSE) file for details.

### Commercial Use
For commercial use, including but not limited to using this code in commercial products, services, or any revenue-generating activities, please contact asifpatankar@rocketmail.com to obtain a commercial license.

Commercial users have the following options:
- One-time licensing fee
- Revenue sharing arrangement
- Repository sponsorship
- Custom licensing terms

All commercial inquiries will be handled on a case-by-case basis.
