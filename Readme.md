# Advanced EXIF Metadata Extractor

## Overview

This project is an advanced EXIF metadata extractor tool built with Streamlit. It provides a comprehensive suite of features for analyzing EXIF metadata in images, including extracting GPS coordinates, checking for hidden messages through steganography, analyzing timestamp inconsistencies, and exporting metadata to a JSON file.

## Features

- **EXIF Data Extraction:** Retrieve detailed EXIF metadata from uploaded images.
- **GPS Coordinates:** Extract and display GPS coordinates, with reverse geocoding to convert them into a human-readable address.
- **Timestamp Analysis:** Analyze image timestamps to detect potential modifications.
- **Camera and Lens Information:** Display detailed information about the camera and lens used to capture the image.
- **File Integrity:** Compute and display the SHA-256 hash of the uploaded file to verify its integrity.
- **Steganography Check:** Detect and reveal any hidden messages in the image using steganography techniques.
- **Metadata Export:** Export the extracted metadata to a downloadable JSON file.


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/advanced-exif-metadata-extractor.git
    ```

2. Navigate to the project directory:
    ```bash
    cd advanced-exif-metadata-extractor
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

2. Open your web browser and go to `http://localhost:8501` to access the tool.

3. Upload an image file to extract its EXIF metadata and use the available features.

## Dependencies

- `Pillow` - For image processing and EXIF metadata extraction.
- `requests` - For making HTTP requests to reverse geocoding services.
- `pandas` - For handling GPS coordinates and displaying them on a map.
- `stegano` - For detecting hidden messages using steganography.
- `streamlit` - For building the web interface.

