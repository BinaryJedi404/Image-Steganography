import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from steganogan import SteganoGAN

# Function to select an image


def select_image():
    global image_path
    image_path = filedialog.askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
    if image_path:
        image = Image.open(image_path)
        image.thumbnail((300, 300))
        photo = ImageTk.PhotoImage(image)
        canvas.itemconfig(image_preview, image=photo)
        canvas.image = photo
        hide_button.configure(state=tk.NORMAL)
        extract_button.configure(state=tk.NORMAL)

# Function to hide a message using LSB steganography


def hide_message_lsb(image_path, message):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    message_bin = ''.join(format(ord(c), '08b') for c in message)
    message_len = len(message_bin)
    max_message_len = (width * height * 3) // 8
    if message_len > max_message_len:
        raise ValueError("Message is too long to fit in image.")
    message_bin += '0' * (8 - message_len % 8)
    pixels = list(img.getdata())
    new_pixels = []
    message_idx = 0
    for pixel in pixels:
        if message_idx < message_len:
            new_pixel = (
                pixel[0] & ~1 | int(message_bin[message_idx]),
                pixel[1] & ~1 | int(message_bin[message_idx + 1]),
                pixel[2] & ~1 | int(message_bin[message_idx + 2])
            )
            message_idx += 3
        else:
            new_pixel = pixel
        new_pixels.append(new_pixel)
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(new_pixels)
    return new_img
# Function to extract a hidden message using LSB steganography


def extract_message_lsb(image_path):
    img = Image.open(image_path).convert("RGB")
    pixels = list(img.getdata())
    message_bin = ""
    for pixel in pixels:
        message_bin += str(pixel[0] & 1)
        message_bin += str(pixel[1] & 1)
        message_bin += str(pixel[2] & 1)
    message = ""
    for i in range(0, len(message_bin), 8):
        byte = message_bin[i:i+8]
        char = chr(int(byte, 2))
        if char == '\0':
            break
        message += char
    return message


def hide_message_gan(image_path, message):
    steganogan = SteganoGAN.load(architecture='dense')
    steganogan.encode(image_path, r'C:\Users\verma\OneDrive\Desktop\CNS PROJECT\output.png', message)


def extract_message_gan(image_path):
    steganogan = SteganoGAN.load(architecture='dense')
    return steganogan.decode(image_path)

# Function to handle the "Hide Message" button click


def hide_message_click():
    message = message_input.get("1.0", "end-1c")
    if selected_method.get() == "LSB":
        try:
            hidden_img = hide_message_lsb(image_path, message)
            save_path = filedialog.asksaveasfilename(defaultextension=".png")
            hidden_img.save(save_path)
            messagebox.showinfo(
                "Success", "Message hidden in image and saved to file.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    elif selected_method.get() == "GAN":
        hide_message_gan(image_path, message)
        messagebox.showinfo(
            "Success", "Message hidden in image and saved to file.")

# Function to handle the "Extract Message" button click


def extract_message_click():
    if selected_method.get() == "LSB":
        try:
            extracted_message = extract_message_lsb(image_path)
            message_output.config(state=tk.NORMAL)
            message_output.delete("1.0", tk.END)
            message_output.insert(tk.END, extracted_message)
            message_output.config(state=tk.DISABLED)
            messagebox.showinfo("Success", "Message extracted successfully.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    elif selected_method.get() == "GAN":
        extracted_message = extract_message_gan(image_path)
        message_output.config(state=tk.NORMAL)
        message_output.delete("1.0", tk.END)
        message_output.insert(tk.END, extracted_message)
        message_output.config(state=tk.DISABLED)
        messagebox.showinfo("Success", "Message extracted successfully.")


# Create the main window
window = tk.Tk()
window.title("Image Steganography")
window.geometry("400x550")

# Create a canvas for image preview
canvas = tk.Canvas(window, width=300, height=300)
canvas.pack(pady=10)

# Create a button to select an image
select_button = tk.Button(window, text="Select Image", command=select_image)
select_button.pack()

# Create a placeholder image
img = Image.new("RGB", (300, 300), color="white")
photo = ImageTk.PhotoImage(img)
image_preview = canvas.create_image(0, 0, anchor=tk.NW, image=photo)

# Create input for the message
message_label = tk.Label(window, text="Message:")
message_label.pack()
message_input = tk.Text(window, height=5)
message_input.pack()

# Create a dropdown for selecting steganography method
method_label = tk.Label(window, text="Steganography Method:")
method_label.pack()
selected_method = tk.StringVar()
method_dropdown = tk.OptionMenu(window, selected_method, "LSB", "GAN")
method_dropdown.pack()

# Create a button to hide the message
hide_button = tk.Button(window, text="Hide Message",
                        command=hide_message_click, state=tk.DISABLED)
hide_button.pack()

# Create a button to extract the message
extract_button = tk.Button(window, text="Extract Message",
                           command=extract_message_click, state=tk.DISABLED)
extract_button.pack()

# Create a label for the extracted message
message_label = tk.Label(window, text="Extracted Message:")
message_label.pack()

# Create output for the extracted message
message_output = tk.Text(window, height=5, state=tk.DISABLED)
message_output.pack()

# Start the main event loop
window.mainloop()