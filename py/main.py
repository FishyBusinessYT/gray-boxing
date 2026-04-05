import cv2
import struct
import socket

from setup import download_task
from capture_controller import CaptureController
from detector import Detector
from direction_calculator import calculate_directions

download_task()

detector = Detector()
captcont = CaptureController()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    timestamp, mp_image = captcont.get_frame()
    landmarks = detector.get_landmarks(mp_image, timestamp).pose_landmarks[0]
    node_directions = calculate_directions(landmarks)

    data = struct.pack('57f', *node_directions)
    server_socket.sendto(data, ('127.0.0.1', 52346))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

server_socket.close()
detector.cleanup()
captcont.cleanup()
