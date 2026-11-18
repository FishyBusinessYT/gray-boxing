import argparse
import struct
import socket

from setup import download_task
from capture_controller import CaptureController, draw_landmarks_on_image, LandmarkPlotter
from detector import Detector
from direction_calculator import calculate_directions


def parse_args():
    parser = argparse.ArgumentParser(description="Gray Boxing motion capture backend.")
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="VideoCapture device index to open (default: 0).",
        )
    return parser.parse_args()


args = parse_args()

download_task()

dtr = Detector()
captcont = CaptureController(args.camera_index)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

failed_frames = 0
processed_frames = 0
skip_ratio = 1 / 3

plotter = LandmarkPlotter()

while True:  # TODO handle exit properly
    # If the camera frames aren't continually consumed, they generate latency
    timestamp, mp_image = captcont.get_frame()

    if processed_frames >= 1:
        processed_frames = 0
    else:
        processed_frames += skip_ratio
        continue

    try:
        detection_result = dtr.get_landmarks(mp_image, timestamp)
        landmarks = detection_result.pose_world_landmarks[0]
        #draw_landmarks_on_image(mp_image.numpy_view(), detection_result.pose_landmarks)
        plotter.plot(detection_result.pose_landmarks[0])
        node_directions = calculate_directions(landmarks)

        data = struct.pack("54f", *node_directions)

        failed_frames = 0

    except IndexError:
        data = struct.pack("7s", b"plyr404")

        failed_frames += 1
        if failed_frames >= 100:
            print(f"Lost sight of player (f#{failed_frames}).")

    server_socket.sendto(data, ("127.0.0.1", 52346))

server_socket.close()
dtr.cleanup()
captcont.cleanup()
