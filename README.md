# Car Plate Detector & Parking Management System

A comprehensive desktop system for parking management, combining a modern graphical interface (PyQt5) with computer vision (OpenCV, Tesseract OCR), and a database (PostgreSQL). The application allows scanning license plates at entry, calculating parking duration based on editable taxes, and processing payments via QR codes.

## Requirements

- Python 3.10+
- Tesseract OCR (Set the path in your code, usually `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- PostgreSQL
- ZBar (for QR code scanning - `pyzbar`)

Before using the system, install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Launch the GUI application:
```bash
python src/gui/gui_interface.py
```

*(Note: Images for testing can be found in the `img/` directory, and generated QR codes will be saved in `qrcodes/`)*

### Key Features

- **Graphical Interface (PyQt5)**: Fast and intuitive system with User mode (for entry/exit/payment scans) and Administrator mode (for logs and settings), styled with CSS.
- **Native Dark Mode**: Automatic support for window title bars (Windows DWM API) and modern widget design.
- **Automatic Plate Detection**: Live camera or uploaded video input, with contour analysis, aspect-ratio filtering, and EU flag removal to accurately identify license plates.
- **Payment and Exit (QR Codes)**: Generation of temporary tickets with scannable QR codes for payment processing, plus live camera scanning for payment and exit.
- **Database (PostgreSQL)**: Chronological management of vehicles, visit logging, and dynamic duration-based taxation.
- **Dynamic Taxes (Admin)**: Secure interface to edit pricing and time parameters.
- **Async Processing (Threading)**: Background workers for image processing (LPR, QR) without freezing the GUI.
- **Debug Mode**: Comprehensive logging and generation of intermediate images (blur, contours) in `debug_output/` for troubleshooting OCR steps.

### Project Structure

```text
Licenta/
├── src/                    
│   ├── main.py                    # Application entry point
│   ├── db/                        # Database integration
│   │   └── db.py                 
│   ├── detector/                  # Back-End Computer Vision & LPR
│   │   ├── contour_analyzer.py 
│   │   ├── image_processor.py  
│   │   ├── license_plate_detector.py
│   │   ├── ocr_engine.py       
│   │   └── debug_manager.py       
│   └── gui/                       # Front-End GUI (PyQt5)
│       ├── gui_interface.py       # Main Window and routing logic
│       ├── admin_logic.py         # Admin tabs (Taxes/Cars)
│       ├── user_logic.py          # User actions (Enter/Pay/Leave)
│       ├── utils.py               # Windows Theme & Background Threads
│       └── styles.css             # Component styling
├── img/                           # Reference images
├── qrcodes/                       # Output folder for generated QR tickets
├── debug_output/                  # Output for DEBUG mode
└── requirements.txt               # Dependencies
```

### Example photos

<p align="center">
  <img src="img/Examples/example%20(1).jpg" width="48%" alt="Example 1" />
  <img src="img/Examples/example%20(2).jpg" width="48%" alt="Example 2" />
</p>
<p align="center">
  <img src="img/Examples/example%20(3).jpg" width="48%" alt="Example 3" />
  <img src="img/Examples/example%20(4).jpg" width="48%" alt="Example 4" />
</p>
