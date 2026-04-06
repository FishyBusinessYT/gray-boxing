import sys
import os

# Add sys._MEIPASS to PATH so native libs resolve.
if hasattr(sys, '_MEIPASS'):
    bundle_dir = sys._MEIPASS
    os.environ['PATH'] = bundle_dir + os.pathsep + os.environ.get('PATH', '')

    # Pin CWD to the bundle root
    os.chdir(bundle_dir)
