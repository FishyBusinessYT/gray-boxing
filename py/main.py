import cv2
import struct
import socket

from setup import download_task
from capture_controller import CaptureController
from detector import Detector
from direction_calculator import calculate_directions

download_task()

dtr = Detector()
captcont = CaptureController()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

failed_frames = 0

while True:
    timestamp, mp_image = captcont.get_frame()
    try:
        landmarks = dtr.get_landmarks(mp_image, timestamp).pose_landmarks[0]
        node_directions = calculate_directions(landmarks)

        data = struct.pack('57f', *node_directions)

        failed_frames = 0

    except IndexError:
        data = struct.pack('7s', b'plyr404')

        failed_frames += 1
        if failed_frames >= 100:
            print(f'Lost sight of player (f#{failed_frames}).')

    server_socket.sendto(data, ('127.0.0.1', 52346))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

server_socket.close()
dtr.cleanup()
captcont.cleanup()
