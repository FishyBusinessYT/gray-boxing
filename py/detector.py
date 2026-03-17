from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class Detector:
    def __init__(self):
        base_options = python.BaseOptions(
            model_asset_path='pose_landmarker_full.task'
            )
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=0.7,
            min_pose_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            )

        self.landmarker = vision.PoseLandmarker.create_from_options(options)

    def get_landmarks(self, mp_image, timestamp):
        return self.landmarker.detect_for_video(mp_image, timestamp)

    def cleanup(self):
        self.landmarker.close()
