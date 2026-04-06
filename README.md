# Gray Boxing
A boxing game where your character mimics your own motions.

## Development Environment Setup

### Prerequisites

Before setting up the development environment, ensure you have the following installed:

- **Godot Engine** (latest)
- **UV (Python project manager)** (latest)

### Setup

1. Clone the repository locally:
    ```bash
    git clone git@github.com:FishyBusinessYT/gray-boxing.git
    ```
2. Navigate to the `py/` directory:
    ```bash
    cd ./gray-boxing/py
    ```
3. Setup the Python development environment using UV:
    ```bash
    uv sync
    ```

#### Before running the Godot project:
1. Navigate to the Python project and build:
    ```
    cd ./gray-boxing/py
    uv run pyinstaller main.spec
    ```
2. Create a symlink to the resulting file:
    ```bash
    cd ./gray-boxing/godot-project
    ln -s ../py/dist/gray_boxing_input/gray_boxing_input ./gray_boxing_input
    ```
The symlink is not included in the final build, but will allow the project to 
run in the editor.

### Export

#### Linux
1. Navigate to the `godot-project` folder and execute the following command:
    ```bash
    godot --export-release Linux ../export/linux/GrayBoxing.x86_64
    ```
2. Build the Python project as noted above
3. Type `y`, then `Enter` to replace old files if prompted
4. While still in the `py` directory, copy the build result into the export folder:
    ```bash
    cp -r ./dist/gray_boxing_input/backend ./dist/gray_boxing_input/lib ../export/linux/
    ```

#### Windows (PENDING)

## Running the Game
### Linux
Navigate to the game installation folder and execute the `GrayBoxing.x86_64` binary.
