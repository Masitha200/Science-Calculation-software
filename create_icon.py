import os
from PIL import Image, ImageDraw

def create_app_icon():
    # Create a 256x256 image with a dark space background
    size = (256, 256)
    img = Image.new("RGBA", size, "#0f0f1b")
    draw = ImageDraw.Draw(img)
    
    # Draw atom rings (cyan circles)
    # Ring 1
    draw.ellipse([28, 28, 228, 228], outline="#00e5ff", width=6)
    # Ring 2 (tilted or ellipse)
    draw.ellipse([50, 20, 206, 236], outline="#bd00ff", width=4)
    
    # Draw central nucleus (green)
    draw.ellipse([110, 110, 146, 146], fill="#00ff88", outline="#ffffff", width=2)
    
    # Draw some orbiting electrons
    draw.ellipse([24, 120, 36, 132], fill="#00e5ff")
    draw.ellipse([220, 120, 232, 132], fill="#00e5ff")
    draw.ellipse([80, 26, 92, 38], fill="#bd00ff")
    draw.ellipse([176, 226, 188, 238], fill="#bd00ff")
    
    # Draw sine wave graph across bottom
    points = []
    for x in range(30, 226):
        import math
        # y = A * sin(k*x) + offset
        y = 180 + 20 * math.sin((x - 30) * 0.08)
        points.append((x, y))
        
    draw.line(points, fill="#ffae00", width=4)

    # Save as ICO (supports multiple sizes automatically)
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    img.save(icon_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print(f"Icon file created successfully at: {icon_path}")

if __name__ == "__main__":
    create_app_icon()
