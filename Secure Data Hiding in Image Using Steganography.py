import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np

# Character mappings
char_to_int = {chr(i): i for i in range(255)}
int_to_char = {i: chr(i) for i in range(255)}

def encode_message(image_path, message, password):
    """Encodes a secret message into an image using LSB steganography."""
    img = cv2.imread(image_path)
    if img is None:
        messagebox.showerror("Error", "Image not found!")
        return False

    secret_data = password + ":" + message  # Store password with message
    binary_msg = ''.join(format(char_to_int[char], '08b') for char in secret_data)
    binary_msg += '00000000'  # End marker

    index = 0
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            for color in range(3):  # Iterate over R, G, B
                if index < len(binary_msg):
                    pixel_value = int(img[row, col, color])
                    new_value = (pixel_value & ~1) | int(binary_msg[index])
                    img[row, col, color] = max(0, min(255, new_value))
                    index += 1
                else:
                    break
            if index >= len(binary_msg):
                break
        if index >= len(binary_msg):
            break

    encrypted_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All Files", "*.*")]
    )

    if not encrypted_path:
        messagebox.showinfo("Canceled", "Saving canceled.")
        return False

    cv2.imwrite(encrypted_path, img)
    messagebox.showinfo("Success", f"Message hidden successfully!\nSaved at: {encrypted_path}")
    return True

def decode_message(image_path, password):
    """Decodes a hidden message from an image using LSB steganography."""
    img = cv2.imread(image_path)
    if img is None:
        messagebox.showerror("Error", "Image not found!")
        return None

    binary_msg = ""
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            for color in range(3):  # Iterate over R, G, B
                binary_msg += str(img[row, col, color] & 1)
                if binary_msg[-8:] == "00000000":
                    break
            if binary_msg[-8:] == "00000000":
                break
        if binary_msg[-8:] == "00000000":
            break

    binary_msg = binary_msg[:-8]
    decoded_msg = "".join(int_to_char[int(binary_msg[i:i+8], 2)] for i in range(0, len(binary_msg), 8))

    if ":" not in decoded_msg:
        messagebox.showerror("Error", "Corrupted data or incorrect password!")
        return None

    stored_password, secret_message = decoded_msg.split(":", 1)

    if stored_password != password:
        messagebox.showerror("Error", "Incorrect password!")
        return None

    return secret_message

# GUI Functions
def open_encode_window():
    encode_window = tk.Toplevel(root)
    encode_window.title("Encode Message")
    encode_window.geometry("400x300")

    tk.Label(encode_window, text="Enter Secret Message:", font=("Arial", 11)).pack(pady=5)
    message_entry = tk.Text(encode_window, height=4, width=40)
    message_entry.pack()

    tk.Label(encode_window, text="Enter Passcode:", font=("Arial", 11)).pack(pady=5)
    password_entry = tk.Entry(encode_window, show="*")
    password_entry.pack()

    def encode_action():
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not image_path:
            return
        message = message_entry.get("1.0", tk.END).strip()
        password = password_entry.get()
        
        if not message or not password:
            messagebox.showerror("Error", "Message and password are required!")
            return
        
        if encode_message(image_path, message, password):
            messagebox.showinfo("Success", "Message encoded successfully!")

    tk.Button(encode_window, text="Select Image & Encode", command=encode_action, bg="lightblue", fg="black").pack(pady=10)

def open_decode_window():
    decode_window = tk.Toplevel(root)
    decode_window.title("Decode Message")
    decode_window.geometry("400x200")

    tk.Label(decode_window, text="Enter Passcode:", font=("Arial", 11)).pack(pady=5)
    password_entry = tk.Entry(decode_window, show="*")
    password_entry.pack()

    def decode_action():
        image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if not image_path:
            return
        password = password_entry.get()
        
        if not password:
            messagebox.showerror("Error", "Password is required for decryption!")
            return
        
        decoded_msg = decode_message(image_path, password)
        if decoded_msg:
            messagebox.showinfo("Decrypted Message", decoded_msg)
        else:
            messagebox.showerror("Error", "Failed to decode the message.")

    tk.Button(decode_window, text="Select Image & Decode", command=decode_action, bg="lightgreen", fg="black").pack(pady=10)

# Main GUI
root = tk.Tk()
root.title("Image Steganography")
root.geometry("400x250")

tk.Label(root, text="Choose an Option", font=("Arial", 12, "bold")).pack(pady=20)
tk.Button(root, text="Encode Message", command=open_encode_window, bg="blue", fg="white", width=20, height=2).pack(pady=10)
tk.Button(root, text="Decode Message", command=open_decode_window, bg="green", fg="white", width=20, height=2).pack(pady=10)

# Run GUI
root.mainloop()
