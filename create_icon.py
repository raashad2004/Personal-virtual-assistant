import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def create_assistant_icon():
    """
    Create a professional-looking icon for the Voice Assistant application
    """
    print("Creating application icon...")
    
    # Create assets directory if it doesn't exist
    if not os.path.exists("assets"):
        os.makedirs("assets")
    
    # Icon parameters
    icon_size = (512, 512)
    bg_color = (52, 73, 94)  # Dark blue background
    accent_color = (52, 152, 219)  # Light blue accent
    highlight_color = (46, 204, 113)  # Green highlight
    
    # Create base image with background
    img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a rounded rectangle for background
    # Since PIL doesn't have direct rounded rectangle, we'll create it using multiple elements
    padding = 20
    radius = 80
    
    # Draw the main circle (background)
    center_x, center_y = icon_size[0] // 2, icon_size[1] // 2
    circle_radius = min(center_x, center_y) - padding
    
    draw.ellipse((center_x - circle_radius, center_y - circle_radius,
                 center_x + circle_radius, center_y + circle_radius),
                fill=bg_color)
    
    # Draw microphone
    mic_width = circle_radius * 0.45
    mic_height = circle_radius * 0.8
    mic_top = center_y - mic_height // 2
    mic_bottom = center_y + mic_height // 2
    mic_left = center_x - mic_width // 2
    mic_right = center_x + mic_width // 2
    
    # Microphone head (rounded rectangle)
    # Top semi-circle
    draw.ellipse((mic_left, mic_top, mic_right, mic_top + mic_width),
                fill=accent_color)
    
    # Bottom semi-circle
    draw.ellipse((mic_left, mic_bottom - mic_width, mic_right, mic_bottom),
                fill=accent_color)
    
    # Rectangle body
    draw.rectangle((mic_left, mic_top + mic_width // 2,
                  mic_right, mic_bottom - mic_width // 2),
                fill=accent_color)
    
    # Microphone stand
    stand_width = mic_width * 0.2
    stand_height = mic_height * 0.4
    stand_top = mic_bottom
    stand_bottom = stand_top + stand_height
    
    draw.rectangle((center_x - stand_width // 2, stand_top,
                  center_x + stand_width // 2, stand_bottom),
                fill=accent_color)
    
    # Stand base
    base_width = mic_width * 0.8
    base_height = stand_height * 0.15
    
    draw.rectangle((center_x - base_width // 2, stand_bottom - base_height,
                  center_x + base_width // 2, stand_bottom),
                fill=accent_color)
    
    # Draw sound waves
    wave_count = 3
    wave_gap = circle_radius * 0.15
    max_wave_thickness = 5
    
    for i in range(wave_count):
        wave_radius = mic_right + wave_gap * (i + 1)
        wave_thickness = max(1, max_wave_thickness - i)
        
        # Draw a partial circle for the wave (on both sides)
        # Left side wave
        draw.arc((center_x - wave_radius, center_y - wave_radius,
                center_x + wave_radius, center_y + wave_radius),
               230, 310, fill=highlight_color, width=wave_thickness)
        
        # Right side wave
        draw.arc((center_x - wave_radius, center_y - wave_radius,
                center_x + wave_radius, center_y + wave_radius),
               50, 130, fill=highlight_color, width=wave_thickness)
    
    # Add a subtle inner glow
    glow = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.alpha_composite(glow, img)
    
    # Save as ICO file
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon_path = "assets/icon.ico"
    
    # Resize for ICO format
    resized_images = []
    for size in icon_sizes:
        resized = img.resize(size, Image.LANCZOS)
        resized_images.append(resized)
    
    # Save the icon
    resized_images[0].save(
        icon_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in resized_images]
    )
    
    print(f"Icon created successfully at {icon_path}")
    
    # Also save as PNG for documentation
    img.save("assets/icon.png", format="PNG")
    print("PNG version also saved to assets/icon.png")
    
    return icon_path

if __name__ == "__main__":
    try:
        icon_path = create_assistant_icon()
        print(f"You can now use this icon in your application by referencing: {icon_path}")
    except Exception as e:
        print(f"Error creating icon: {str(e)}")
        print("Please ensure you have Pillow installed: pip install Pillow") 