import struct
import socket

from setup import download_task
from capture_controller import CaptureController, draw_landmarks_on_image
from detector import Detector
from direction_calculator import calculate_directions

download_task()

dtr = Detector()
captcont = CaptureController()
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

failed_frames = 0
processed_frames = 0
skip_ratio = 1 / 3

while True: # TODO handle exit properly
    # If the camera frames aren't continually consumed, they generate latency
    timestamp, mp_image = captcont.get_frame()

    if processed_frames >= 1:
        processed_frames = 0
    else:
        processed_frames += skip_ratio
        continue
    
    try:
        landmarks = dtr.get_landmarks(mp_image, timestamp).pose_landmarks[0]

        node_directions = calculate_directions(landmarks)
        data = struct.pack('51f', *node_directions)

        #draw_landmarks_on_image(mp_image.numpy_view(), [landmarks])
        
        failed_frames = 0

    except IndexError:
        data = struct.pack('7s', b'plyr404')

        failed_frames += 1
        if failed_frames >= 100:
            print(f'Lost sight of player (f#{failed_frames}).')

    server_socket.sendto(data, ('127.0.0.1', 52346))

server_socket.close()
dtr.cleanup()
captcont.cleanup()
