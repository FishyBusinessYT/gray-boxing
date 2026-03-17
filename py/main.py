import cv2

from setup import download_task
from capture_controller import CaptureController
from detector import Detector
from draw import draw_landmarks_on_image

download_task()

detector = Detector()
captcont = CaptureController()

while True:
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    timestamp, img, mp_image = captcont.get_frame()
    result = detector.get_landmarks(mp_image, timestamp)

    try:
        annotated_image = draw_landmarks_on_image(
            mp_image.numpy_view(), result
            )
        cv2.imshow("window", cv2.cvtColor(
            annotated_image, cv2.COLOR_RGB2BGR)
            )

    except UnboundLocalError:
        cv2.imshow("window", img)

detector.cleanup()
captcont.cleanup()
