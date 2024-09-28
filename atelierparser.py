import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageOps, ImageTk
import sqlite3
import io
import os
import sys

# Global variables
img_path = None
img_preview = None

# Define constants for the script
image_format = "PNG"
image_mode = "LA"
image_info = {}
target_width = 1536
target_height = 2048
tile_width, tile_height = 128, 128  # Tile dimensions for the grid
rows, cols = 16, 12  # Number of rows and columns in the grid
tids = [
    7976857, 7980953, 7985049, 7989145, 7993241, 7997337, 8001433, 8005529, 8009625, 8013721, 8017817, 8021913,
    7976858, 7980954, 7985050, 7989146, 7993242, 7997338, 8001434, 8005530, 8009626, 8013722, 8017818, 8021914,
    7976859, 7980955, 7985051, 7989147, 7993243, 7997339, 8001435, 8005531, 8009627, 8013723, 8017819, 8021915,
    7976860, 7980956, 7985052, 7989148, 7993244, 7997340, 8001436, 8005532, 8009628, 8013724, 8017820, 8021916,
    7976861, 7980957, 7985053, 7989149, 7993245, 7997341, 8001437, 8005533, 8009629, 8013725, 8017821, 8021917,
    7976862, 7980958, 7985054, 7989150, 7993246, 7997342, 8001438, 8005534, 8009630, 8013726, 8017822, 8021918,
    7976863, 7980959, 7985055, 7989151, 7993247, 7997343, 8001439, 8005535, 8009631, 8013727, 8017823, 8021919,
    7976864, 7980960, 7985056, 7989152, 7993248, 7997344, 8001440, 8005536, 8009632, 8013728, 8017824, 8021920,
    7976865, 7980961, 7985057, 7989153, 7993249, 7997345, 8001441, 8005537, 8009633, 8013729, 8017825, 8021921,
    7976866, 7980962, 7985058, 7989154, 7993250, 7997346, 8001442, 8005538, 8009634, 8013730, 8017826, 8021922,
    7976867, 7980963, 7985059, 7989155, 7993251, 7997347, 8001443, 8005539, 8009635, 8013731, 8017827, 8021923,
    7976868, 7980964, 7985060, 7989156, 7993252, 7997348, 8001444, 8005540, 8009636, 8013732, 8017828, 8021924,
    7976869, 7980965, 7985061, 7989157, 7993253, 7997349, 8001445, 8005541, 8009637, 8013733, 8017829, 8021925,
    7976870, 7980966, 7985062, 7989158, 7993254, 7997350, 8001446, 8005542, 8009638, 8013734, 8017830, 8021926,
    7976871, 7980967, 7985063, 7989159, 7993255, 7997351, 8001447, 8005543, 8009639, 8013735, 8017831, 8021927,
    7976872, 7980968, 7985064, 7989160, 7993256, 7997352, 8001448, 8005544, 8009640, 8013736, 8017832, 8021928
]

# Define maximum allowed padding constraints
max_left_padding = 9
max_top_padding = 78
max_right_padding = 109
max_bottom_padding = 84

# Define the target dimensions
target_width = 1536
target_height = 2048

# Preprocess the image (convert, resize, and pad/crop)
def preprocess_image(image_path):
    # Load the original image and correct Exif rotation if present
    original_image = Image.open(image_path)
    original_image = ImageOps.exif_transpose(original_image)

    # Convert the image to the specified mode (e.g., LA - grayscale with alpha channel)
    # Use RGBA mode initially to retain transparency during padding/cropping
    if original_image.mode not in ["LA", "RGBA"]:
        original_image = original_image.convert("RGBA")

    # Create a blank image with transparent background for the target size
    new_image = Image.new("LA", (target_width, target_height), (0, 0))  # Transparent background

    # Get the original dimensions after conversion
    original_width, original_height = original_image.size

    # Calculate default padding to center the image within the target canvas
    pad_left = (target_width - original_width) // 2
    pad_top = (target_height - original_height) // 2

    # Apply padding constraints
    pad_left = min(pad_left, max_left_padding)
    pad_right = target_width - original_width - pad_left
    pad_right = min(pad_right, max_right_padding)

    pad_top = min(pad_top, max_top_padding)
    pad_bottom = target_height - original_height - pad_top
    pad_bottom = min(pad_bottom, max_bottom_padding)

    # Calculate the position to paste the original image onto the new transparent canvas
    paste_x = pad_left + (target_width - pad_left - pad_right - original_width) // 2
    paste_y = pad_top + (target_height - pad_top - pad_bottom - original_height) // 2

    # Paste the original image onto the new transparent background, centered
    new_image.paste(original_image, (paste_x, paste_y), original_image)

    # Return the final preprocessed image
    return new_image

# Split image into tiles and save them in SQLite
def split_image_into_tiles(image_path, database_path):
    # Preprocess the image
    image = preprocess_image(image_path)

    # Set the tile size and calculate rows and columns
    tile_width, tile_height = 128, 128
    rows, cols = 16, 12

    # Create or connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Create tables if they do not exist
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS "surface_1" (
            "tid" INTEGER NOT NULL,
            "tile" BLOB NOT NULL,
            PRIMARY KEY("tid")
        ) WITHOUT ROWID;

        CREATE TABLE IF NOT EXISTS "surface_2" (
            "tid" INTEGER NOT NULL,
            "tile" BLOB NOT NULL,
            PRIMARY KEY("tid")
        ) WITHOUT ROWID;

        CREATE TABLE IF NOT EXISTS "config" (
            "name" TEXT PRIMARY KEY NOT NULL,
            "value" BLOB
        );
    ''')

    # Insert hardcoded config entries
    config_entries = {
        "fmt_ver": 2,
        "ls": bytes.fromhex("0a0b080212074c6179657220310a0e0801120a4261636b67726f756e6410021802"),  
        "thumbnail": b"",
        "vp.x": 249984.0,
        "vp.y": 249984.0,
        "vp.scale": 1.0,
        "frames": b""
    }
    cursor.executemany(
        'INSERT OR REPLACE INTO config (name, value) VALUES (?, ?)',
        [(key, value if isinstance(value, bytes) else str(value).encode('utf-8')) for key, value in config_entries.items()]
    )

    # Split and insert image tiles
    tile_index = 0
    for row in range(rows):
        for col in range(cols):
            if tile_index >= len(tids):
                break
            # Crop the image to get a tile
            box = (col * tile_width, row * tile_height, (col + 1) * tile_width, (row + 1) * tile_height)
            tile = image.crop(box)

            # Save tile as bytes
            tile_bytes = io.BytesIO()
            tile.save(tile_bytes, format=image_format, **image_info)
            tile_data = tile_bytes.getvalue()

            # Insert tile into surface_1
            cursor.execute(
                'INSERT OR IGNORE INTO surface_1 (tid, tile) VALUES (?, ?)',
                (tids[tile_index], tile_data)
            )
            tile_index += 1

    # Finalize and rename database
    conn.commit()
    conn.close()
    
    # Ensure the new database path ends with .spd without duplicating the extension
    if not database_path.endswith(".spd"):
        new_database_path = os.path.splitext(database_path)[0] + ".spd"
    else:
        new_database_path = database_path
    
    # If the file already exists, remove it to prevent errors
    if os.path.exists(new_database_path):
        os.remove(new_database_path)
    
    # Rename the temporary .db file to .spd file
    os.rename(database_path, new_database_path)
    
    messagebox.showinfo("Success", f"Image split into {tile_index} tiles and saved as {new_database_path}.")

# Function to handle Confirm button click
def on_confirm():
    global img_path
    if img_path:
        # Open the save file dialog to select where to save the .spd file
        save_path = filedialog.asksaveasfilename(
            defaultextension=".spd",
            filetypes=[("SQLite Database", "*.spd")],
            title="Save .spd File"
        )

        if save_path:
            # Ensure the save_path does not have a double .spd extension
            if save_path.endswith(".spd"):
                temp_db_path = save_path.replace(".spd", ".db")
            else:
                temp_db_path = save_path + ".db"
            
            # Call the function to process the image and create the .spd file
            split_image_into_tiles(img_path, temp_db_path)

            # After saving, reset the UI back to the browse state
            cancel_selection()

# Function to load and preview the image
def load_image(file_path):
    global img_path, img_preview
    img_path = file_path
    try:
        # Open and display the image in the preview area
        img = Image.open(img_path)
        img.thumbnail((400, 400))  # Resize image to fit in preview window
        img_preview = ImageTk.PhotoImage(img)

        # Update the preview label with the selected image
        preview_label.config(image=img_preview)

        # Hide the instruction label after an image is selected
        instruction_label.grid_forget()

        # Enable Confirm and Cancel buttons, hide Browse button
        confirm_button.grid(row=0, column=0, padx=10)
        cancel_button.grid(row=0, column=1, padx=10)
        button_frame.grid(row=2, column=0, columnspan=3, pady=20)
        browse_button.grid_forget()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load image: {str(e)}")
        cancel_selection()

# Function to handle file drop
def on_drop(event):
    if event.data:
        file_path = event.data
        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]
        load_image(file_path)

# Function to browse and select an image
def browse_image():
    global img_path
    file_types = [("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.webp")]
    img_path = filedialog.askopenfilename(title="Select an image", filetypes=file_types)
    if img_path:
        load_image(img_path)

# Function to cancel image selection and reset UI
def cancel_selection():
    global img_path, img_preview
    img_path = None
    preview_label.config(image='')  # Clear image preview
    instruction_label.grid(row=0, column=0, columnspan=3, pady=20)  # Show instruction label again
    confirm_button.grid_forget()
    cancel_button.grid_forget()
    button_frame.grid_forget()
    browse_button.grid(row=2, column=0, columnspan=3, sticky='ew', padx=10, pady=10)

# Function to add hover effects to buttons
def on_enter(event, widget):
    widget.config(bg=widget.hover_bg)

def on_leave(event, widget):
    widget.config(bg=widget.default_bg)

# Create the main TkinterDnD window
root = TkinterDnD.Tk()
root.title("AtelierConvert")
root.geometry("600x500")
root.configure(bg="#f0f0f0")  # Set a light background color

# Check if the script is running as a standalone executable
if getattr(sys, 'frozen', False):
    # If running as an executable, get the path to the temp folder
    application_path = sys._MEIPASS
else:
    # If running as a script, use the script directory
    application_path = os.path.dirname(os.path.abspath(__file__))

# Set the icon using a relative path or bundled executable path
icon_path = os.path.join(application_path, "logosmall.ico")
root.iconbitmap(icon_path)

# Configure grid layout for dynamic resizing
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)
root.columnconfigure(2, weight=1)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=1)
root.rowconfigure(2, weight=0)

# Add an instruction label at the top
instruction_label = tk.Label(root, text="Drag and Drop an Image or Browse to Select", font=("Roboto", 16, "bold"), fg="black", bg="#f0f0f0")
instruction_label.grid(row=0, column=0, columnspan=3, pady=20)

# Set up a frame with border for the image preview area
preview_frame = tk.LabelFrame(root, bd=2, relief="ridge", bg="#ffffff")
preview_frame.grid(row=1, column=0, columnspan=3, pady=10, padx=20, sticky='nsew')

# Set up a label inside the frame to show the image preview
preview_label = tk.Label(preview_frame, bg="#ffffff")
preview_label.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
preview_frame.grid_rowconfigure(0, weight=1)
preview_frame.grid_columnconfigure(0, weight=1)

# Create a separate frame for the buttons and place it at the bottom of the window
button_frame = tk.Frame(root, bg="#f0f0f0")
button_frame.grid(row=2, column=0, columnspan=3, pady=10)

# Define styles for buttons
button_style = {
    "font": ("Roboto", 14, "bold"),
    "bd": 1,
    "relief": "flat",
    "highlightthickness": 0,
    "width": 20,
    "height": 2
}

# Browse button
browse_button = tk.Button(root, text="Browse", command=browse_image, bg="#4CAF50", fg="white", **button_style)
browse_button.default_bg = browse_button["bg"]
browse_button.hover_bg = "#66BB6A"  # Lighter green for hover

# Confirm button
confirm_button = tk.Button(button_frame, text="Confirm", command=on_confirm, bg="#007ACC", fg="white", **button_style)
confirm_button.default_bg = confirm_button["bg"]
confirm_button.hover_bg = "#3399FF"  # Lighter blue for hover

# Cancel button
cancel_button = tk.Button(button_frame, text="Cancel", command=cancel_selection, bg="#FF6347", fg="white", **button_style)
cancel_button.default_bg = cancel_button["bg"]
cancel_button.hover_bg = "#FF8C69"  # Lighter red for hover

# Add hover effects for all buttons
for button in [browse_button, confirm_button, cancel_button]:
    button.bind("<Enter>", lambda event, btn=button: on_enter(event, btn))
    button.bind("<Leave>", lambda event, btn=button: on_leave(event, btn))

# Place the browse button after configuring hover effects
browse_button.grid(row=2, column=0, columnspan=3, sticky='ew', padx=10, pady=10)

# Enable drag-and-drop functionality
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# Start the Tkinter main loop
root.mainloop()