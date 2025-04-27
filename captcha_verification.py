import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import tkinter as tk
from tkinter import messagebox

# ✅ Generate Random Text for CAPTCHA
def generate_captcha_text(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# 🎨 Create Distorted CAPTCHA Image
def create_captcha_image(text):
    width, height = 250, 100
    image = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Load Font (Use a font from your system, adjust path as needed)
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except IOError:
        print("Font not found. Ensure 'arial.ttf' is installed.")
        return None

    # Add random lines for distortion
    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill=(random.randint(0, 150), random.randint(0, 150), random.randint(0, 150)), width=2)

    # Draw CAPTCHA text with slight rotation
    for i, char in enumerate(text):
        x = 30 + i * 35
        y = random.randint(10, 40)
        draw.text((x, y), char, font=font, fill=(0, 0, 0))

    # Apply Blur for further distortion
    image = image.filter(ImageFilter.GaussianBlur(1))

    # Save the CAPTCHA image
    image.save("captcha.png")
    return image

# 🧪 Verify CAPTCHA Input
def verify_captcha():
    user_input = entry.get().strip()
    if user_input == captcha_text:
        messagebox.showinfo("✅ Verification", "Human Verified!")
    else:
        messagebox.showerror("❌ Verification Failed", "Incorrect CAPTCHA. Please try again.")
        reset_captcha()

# 🔄 Reset CAPTCHA
def reset_captcha():
    global captcha_text
    captcha_text = generate_captcha_text()
    create_captcha_image(captcha_text)
    captcha_img = tk.PhotoImage(file="captcha.png")
    captcha_label.config(image=captcha_img)
    captcha_label.image = captcha_img
    entry.delete(0, tk.END)

# 🖥 GUI for CAPTCHA
app = tk.Tk()
app.title("Distorted Text CAPTCHA")

# Generate and Display Initial CAPTCHA
captcha_text = generate_captcha_text()
create_captcha_image(captcha_text)

# Display CAPTCHA Image
captcha_img = tk.PhotoImage(file="captcha.png")
captcha_label = tk.Label(app, image=captcha_img)
captcha_label.pack(padx=10, pady=10)

# CAPTCHA Input Box
entry = tk.Entry(app, font=("Arial", 18))
entry.pack(padx=10, pady=10)

# Submit Button
submit_btn = tk.Button(app, text="Submit", command=verify_captcha, font=("Arial", 14))
submit_btn.pack(pady=10)

# Refresh Button (If CAPTCHA is unclear)
refresh_btn = tk.Button(app, text="Refresh CAPTCHA", command=reset_captcha, font=("Arial", 12))
refresh_btn.pack(pady=5)

app.mainloop()