import asyncio
import time
import subprocess
import logging
from mavsdk import System

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Jetson Nano SSH connection details
JETSON_USER = "<USERNAME>"
JETSON_IP = "<IP_ADDRESS>"
STREAM_SCRIPT_PATH = "/path/to/stream_script.sh"

async def set_script_permissions():
    print("Setting correct permissions for stream script...")
    subprocess.run(["ssh", f"{JETSON_USER}@{JETSON_IP}", f"chmod 755 {STREAM_SCRIPT_PATH}"])

async def start_stream():
    logger.info("Starting video stream...")
    try:
        result = subprocess.run(["ssh", f"{JETSON_USER}@{JETSON_IP}", f"bash {STREAM_SCRIPT_PATH} start"], capture_output=True, text=True, timeout=10)
        logger.info(f"Start stream output: {result.stdout}")
        if result.returncode != 0:
            logger.error(f"Error starting stream: {result.stderr}")
    except subprocess.TimeoutExpired:
        logger.error("Timeout while starting stream")
    except Exception as e:
        logger.error(f"Error starting stream: {str(e)}")

async def stop_stream():
    logger.info("Stopping video stream...")
    try:
        # First, try to stop gracefully
        result = subprocess.run(["ssh", f"{JETSON_USER}@{JETSON_IP}", f"bash {STREAM_SCRIPT_PATH} stop"], capture_output=True, text=True, timeout=10)
        logger.info(f"Stop stream output: {result.stdout}")
        if result.returncode != 0:
            logger.error(f"Error stopping stream: {result.stderr}")

        # Force kill any remaining gst-launch-1.0 processes
        kill_result = subprocess.run(["ssh", f"{JETSON_USER}@{JETSON_IP}", "pkill -f gst-launch-1.0"], capture_output=True, text=True, timeout=5)
        logger.info(f"Force kill output: {kill_result.stdout}")
    except subprocess.TimeoutExpired:
        logger.error("Timeout while stopping stream")
    except Exception as e:
        logger.error(f"Error stopping stream: {str(e)}")

async def main():
    drone = System()
    print("Waiting for drone to connect...")
    await drone.connect(system_address="udp://0.0.0.0:14540") # Adjust as needed for your setup

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected!")
            break

    await set_script_permissions()

    print("Monitoring armed state...")
    last_armed_state = None
    async for is_armed in drone.telemetry.armed():
        if is_armed != last_armed_state:
            if is_armed:
                print("Drone armed!")
                await start_stream()
            else:
                print("Drone disarmed!")
                await stop_stream()
            last_armed_state = is_armed
        await asyncio.sleep(1) # Add a 1-second delay between checks

if __name__ == "__main__":
    asyncio.run(main())
