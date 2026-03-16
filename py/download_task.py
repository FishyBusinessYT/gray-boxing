import os
import urllib.request


def setup():
    url = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
           "pose_landmarker_full/float16/latest/pose_landmarker_full.task")
    filename = "pose_landmarker_full.task"

    if os.path.exists(filename):
        return

    print(f"File '{filename}' doesn't exist. Downloading.")
    urllib.request.urlretrieve(url, filename)
