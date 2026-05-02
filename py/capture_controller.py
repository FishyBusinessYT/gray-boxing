import cv2
import mediapipe as mp


class CaptureController:
    def __init__(self):
        self.capture = cv2.VideoCapture(0)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.current_frame = 0

        # TODO REMOVE THIS WINDOW LATER
        cv2.namedWindow("window")
        cv2.moveWindow("window", 550, 200)

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
