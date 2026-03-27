import cv2

from setup import download_task
from capture_controller import CaptureController
from detector import Detector
from direction_calculator import calculate_directions
from draw import draw_landmarks_on_image

download_task()

detector = Detector()
captcont = CaptureController()

while True:

    timestamp, img, mp_image = captcont.get_frame()
    detector_result = detector.get_landmarks(mp_image, timestamp)
    node_directions = calculate_directions(detector_result.pose_landmarks[0])

    try:
        annotated_image = draw_landmarks_on_image(
            mp_image.numpy_view(), detector_result
            )
        cv2.imshow("window", cv2.cvtColor(
            annotated_image, cv2.COLOR_RGB2BGR)
            )

    except UnboundLocalError:
        cv2.imshow("window", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        for direction_name in node_directions:
            nd = node_directions[direction_name]
            print('\n\n\nDIRNAME:', direction_name, '\n\nVALUES:')
            for i in range(3):
                print(nd[i])
        break


detector.cleanup()
captcont.cleanup()
