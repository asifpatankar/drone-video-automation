#!/bin/bash

log_file="/tmp/stream_script.log"

echo "$(date): Received command: $1" >> $log_file

case $1 in
  start)
    echo "$(date): Starting stream" >> $log_file
    gst-launch-1.0 nvarguscamerasrc ! "video/x-raw(memory:NVMM)",width=1920,height=1080,framerate=30/1,format=NV12 ! videoconvert ! omxh264enc control-rate=constant bitrate=5000000 iframeinterval=15 ! h264parse ! rtph264pay name=pay0 pt=96 config-interval=-1 ! udpsink host=<QGC_IP_ADDRESS> port=5600 sync=false &
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
