import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python.vision import drawing_utils
from mediapipe.tasks.python.vision import drawing_styles
from mediapipe.tasks.python import vision
from matplotlib import pyplot as plt

class CaptureController:
    def __init__(self, camera_index=0):
        self.capture = cv2.VideoCapture(camera_index)
        # Some backends report 0 FPS until the first frame; MediaPipe still
        # needs a monotonically increasing timestamp, so fall back to 30.
        self.fps = self.capture.get(cv2.CAP_PROP_FPS) or 30.0
        self.current_frame = 0

        if not self.capture.isOpened():
            raise RuntimeError(
                f"Could not open camera at index {camera_index}. "
                "Check the device is connected and not in use, or pass a "
                "different index."
                )

    def get_frame(self):
        timestamp = int(self.current_frame/self.fps*1000)
        self.current_frame += 1

        success, img = self.capture.read()

        # We flip the image to make the preview look natural
        img = cv2.flip(img, 1)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            )

        return timestamp, mp_image

    def cleanup(self):
        cv2.destroyAllWindows()
        self.capture.release()

def draw_landmarks_on_image(rgb_image, pose_landmarks_list):
  annotated_image = np.copy(rgb_image)

  pose_landmark_style = drawing_styles.get_default_pose_landmarks_style()
  pose_connection_style = drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=2)

  for pose_landmarks in pose_landmarks_list:
    drawing_utils.draw_landmarks(
        image=annotated_image,
        landmark_list=pose_landmarks,
        connections=vision.PoseLandmarksConnections.POSE_LANDMARKS,
        landmark_drawing_spec=pose_landmark_style,
        connection_drawing_spec=pose_connection_style)

  cv2.imshow("mp", annotated_image)
  cv2.waitKey(1)

class LandmarkPlotter:
    def __init__(self) -> None:
        plt.ion()
        self.fig = plt.figure(figsize=(8, 6))
        self.ax = self.fig.add_subplot(projection='3d')
        for axis, color in zip('xyz', ('red', 'green', 'blue')):
            getattr(self.ax, f'set_{axis}label')(axis.upper(), color=color)
            self.ax.tick_params(axis=axis, colors=color)
            getattr(self.ax, f'{axis}axis').line.set_color(color)
        self.ax.view_init(elev=90, azim=90) # z-axis is pointing front

    def plot(self, landmarks) -> None:
        self.ax.cla()  # limpia el eje, no la figura
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.ax.set_zlim(-1, 1)  # cla() resetea los límites
        self.ax.scatter(
            [lm.x for lm in landmarks],
            [lm.y for lm in landmarks],
            [lm.z for lm in landmarks],
            c='blue',
        )
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(0.001)

    def close(self) -> None:
        plt.ioff()
        plt.close(self.fig)