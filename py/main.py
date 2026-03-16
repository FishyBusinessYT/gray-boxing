import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from download_task import setup
from draw import draw_landmarks_on_image

setup()

base_options = python.BaseOptions(model_asset_path='pose_landmarker_full.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.7,
    min_pose_presence_confidence=0.7,
    min_tracking_confidence=0.7,
    )

cap = cv2.VideoCapture(0)
fps = cap.get(cv2.CAP_PROP_FPS)
current_frame = 0

with vision.PoseLandmarker.create_from_options(options) as landmarker:
    cv2.namedWindow("whatever")
    cv2.moveWindow("whatever", 550, 200)
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        success, img = cap.read()
        img = cv2.flip(img, 1)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            )

        timestamp = int(current_frame/fps*1000)
        landmarker_result = landmarker.detect_for_video(
            mp_image, timestamp
            )

        try:
            annotated_image = draw_landmarks_on_image(
                mp_image.numpy_view(), landmarker_result
                )
            cv2.imshow("whatever", cv2.cvtColor(
                annotated_image, cv2.COLOR_RGB2BGR)
                )

        except UnboundLocalError:
            cv2.imshow("whatever", img)

        current_frame += 1
