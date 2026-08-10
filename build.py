import os
import subprocess
import sys

def build_app():
    print("Starting build process for SciMath Visual Studio...")
    
    # 1. Ensure icon exists
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    if not os.path.exists(icon_path):
        print("Icon file not found. Generating...")
        try:
            import create_icon
            create_icon.create_app_icon()
        except Exception as e:
            print(f"Error generating icon: {e}")
            sys.exit(1)
            
    # 2. Build PyInstaller Command
    # On Windows, PyInstaller path separator for --add-data is ';'
    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--add-data", "icon.ico;.",
        "--icon", "icon.ico",
        "--name", "SciMathStudio",
        "app.py"
    ]
    
    print(f"Executing: {' '.join(command)}")
    
    try:
        subprocess.run(command, check=True)
        print("\n" + "="*50)
        print("BUILD SUCCESSFUL!")
        print("Your standalone desktop package is located at:")
        print(f"  {os.path.join(os.path.dirname(__file__), 'dist', 'SciMathStudio.exe')}")
        print("="*50)
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code: {e.returncode}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: PyInstaller command not found. Install it using 'pip install pyinstaller'.")
        sys.exit(1)

if __name__ == "__main__":
    build_app()
