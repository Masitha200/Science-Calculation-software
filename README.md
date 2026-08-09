# SciMath Visual Studio - Desktop Application

An interactive offline desktop application for visualizing science and mathematics calculations.

## Features
- **Mathematics Studio**:
  - **Function Grapher & Calculus Visualizer**: Plot functions, interact with tangent lines (derivatives) via sliders, and inspect definite integrals (Riemann sums) with adjustable partitions.
  - **Matrix Algebra Visualizer**: Perform matrix operations (determinant, inverse) step-by-step using Gaussian elimination, and watch 2D vector space grids transform dynamically.
- **Physics Sandbox**:
  - **Projectile Kinematics**: Launch projectiles with varying speed, angle, gravity, and air drag. Displays live vector arrows ($v_x, v_y, g$) and trail tracers.
  - **Oscillation Lab**: Interactive pendulum bob (can be clicked and dragged to start a swing) with real-time Potential, Kinetic, and Total Energy bar graphs.
- **Chemistry Lab**:
  - **Periodic Table Explorer**: Interactive chemical elements grid with detailed properties (electronegativities, boiling/melting points, fun facts) and revolving atomic Bohr shell electron orbits.
  - **Stoichiometry Balancer**: Balance chemical equations using linear equation systems and see balanced molecules represented visually as colored atom spheres.

---

## Folder Structure
- `app.py` - The desktop shell wrapper (starts local thread server and opens PyQt5 WebEngine).
- `build.py` - Script to package the application with PyInstaller.
- `create_icon.py` - Script to programmatically generate the neon app icon `icon.ico`.
- `setup.bat` - The Windows installer/setup assistant.
- `src/` - Web frontend assets (HTML, CSS, JS).

---

## How to Install (Using Setup Wizard)

1. Simply run the setup wizard file from the root folder: **`setup.bat`**
2. Confirm the installation path. By default, it will install to:
   `%LOCALAPPDATA%\SciMathStudio`
3. The installer will:
   - Copy the standalone executable to the install folder.
   - Create a desktop shortcut: **`SciMath Studio`**
   - Create a Start Menu shortcut so you can search for "SciMath Studio" in Windows.
   - Create an **`uninstall.bat`** uninstaller script to remove all files and shortcuts if needed.

---

## Development & Bundling Instructions

### Running in Development Mode
You can run the application directly from Python:
```bash
python app.py
```

### Compling standalone EXE again
If you make changes to the visual files in the `src/` folder, rebuild the `.exe` using the builder script:
```bash
python build.py
```
This compiles the application to `dist/SciMathStudio.exe` which can be distributed to other computers.
