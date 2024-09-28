# AtelierConvert

## Description
**AtelierConvert** is a Python tool that makes it easy to turn images into Supernote Atelier-friendly `.spd` files.  
With this tool, you can import any image as a background layer in Atelier, This opens up possibilities for image tracing, using custom templates, grids, and much more.
## Features
- Convert any image (e.g., PNG, JPG, BMP, GIF, WebP) to an `.spd` file.
- Preview images before convertion.
- Simple drag-and-drop functionality.
- Automatic alignment for consistent template formatting.

## Requirements
The executable is standalone and has no requirements—just download and run!
If you prefer to run the Python script rather than the `.exe`, you will need the following dependencies:

- **Python 3.7+**
- **Pillow (PIL)**
- **TkinterDnD2**
- **Tkinter**
- **sqlite3**

You can install the required dependencies using `pip`:

```bash
pip install pillow tk tkinterdnd2
```

## Installation

### For the Precompiled Executable

Simply download the executable from the release section. No installation is required—just run the executable. After saving the `.spd` file, move it to the tablet and open it using Atelier.

### For Running the Python Version

1. Clone or download the repository.
2. Install the dependencies listed in the "Requirements" section.
3. Run the script:

```bash
python atelierconvert.py
```

## Usage

1. **Open the Program**: Launch the executable or run the Python script as described above.
2. **Select an Image**: Drag and drop an image into the window or use the "Browse" button to select an image from your filesystem.
3. **Preview and Confirm**: After selecting an image, a preview will be displayed. Click "Confirm" to proceed.
4. **Save the .spd File**: Choose a location to save the `.spd` file.
5. **Transfer the .spd File**: After saving the `.spd` file, move it to the tablet and open it using Atelier.
   
## License

This project is licensed under the GPL License. See the LICENSE file for more details.

## Acknowledgments

The project utilizes the Pillow library for image processing and TkinterDnD2 for drag-and-drop functionality.
Special thanks to the Supernote community for their support and feedback on all my projects, with special thanks to @mmujynya for his support and development of PySN.
Additionally, I would like to thank the Supernote team for all their hard work and dedication to the community.
