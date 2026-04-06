# gray_boxing_input.spec
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

block_cipher = None

hidden_imports = [
    *collect_submodules('mediapipe'),
    *collect_submodules('google.protobuf'),
    *collect_submodules('absl'),
]

datas = [
    *collect_data_files('mediapipe'),   # internal graph/model assets
    *collect_data_files('cv2'),         # haarcascades, etc.
    ('pose_landmarker_full.task', '.'),
]

binaries = [
    *collect_dynamic_libs('mediapipe'),
    *collect_dynamic_libs('cv2'),
]

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    runtime_hooks=['rthook.py'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='gray_boxing_input',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='gray_boxing_input',
)
