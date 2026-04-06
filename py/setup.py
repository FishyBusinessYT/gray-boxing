import os
import sys
import urllib.request


def download_task():
    filename = "pose_landmarker_full.task"

    # When frozen by PyInstaller, the .task file is already bundled into
    # sys._MEIPASS, so it'll exist.
    if os.path.exists(filename):
        return

    # If frozen but the file is missing anyway, raise a clear error rather than
    # trying to download it as there's no guarantee of network or write access:
    if getattr(sys, 'frozen', False):
        raise FileNotFoundError(
            f"Bundled model file '{filename}' is missing from the package. "
            "Please re-build the executable."
            )

    print(f"File '{filename}' doesn't exist. Downloading.")
    url = ("https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
           "pose_landmarker_full/float16/latest/pose_landmarker_full.task")
    urllib.request.urlretrieve(url, filename)
