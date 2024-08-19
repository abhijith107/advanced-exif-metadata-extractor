import os
import hashlib
import json
import requests
import pandas as pd
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from PIL.TiffImagePlugin import IFDRational as Rational
import streamlit as st
from datetime import datetime
from stegano import lsb


def convert_exif_data(exif_data):
    """Convert EXIF data to a JSON-serializable format."""
    converted = {}
    for key, value in exif_data.items():
        if isinstance(value, Rational):
            converted[key] = float(value)
        elif isinstance(value, tuple):
            converted[key] = tuple(float(v) if isinstance(v, Rational) else v for v in value)
        else:
            converted[key] = value
    return converted


def get_exif(image_file):
    """Get image file EXIF metadata."""
    img = Image.open(image_file)
    info = img._getexif()

    if not info:
        st.error("No EXIF data found!")
        return None, None

    exif_data = {}
    gps_info = {}

    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            for t in value:
                sub_decoded = GPSTAGS.get(t, t)
                gps_info[sub_decoded] = value[t]
        else:
            if isinstance(value, bytes):
                try:
                    exif_data[decoded] = value.decode("utf-8")
                except UnicodeDecodeError:
                    continue
            else:
                exif_data[decoded] = value

    return convert_exif_data(exif_data), gps_info


def convert_to_degrees(value):
    """Convert GPS coordinates to degrees."""
    d = float(value[0][0]) / float(value[0][1])
    m = float(value[1][0]) / float(value[1][1])
    s = float(value[2][0]) / float(value[2][1])

    return d + (m / 60.0) + (s / 3600.0)


def get_gps_coordinates(gps_info):
    """Extract GPS coordinates from GPSInfo."""
    if not gps_info:
        return None

    gps_latitude = gps_info.get('GPSLatitude')
    gps_latitude_ref = gps_info.get('GPSLatitudeRef')
    gps_longitude = gps_info.get('GPSLongitude')
    gps_longitude_ref = gps_info.get('GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref != "N":
            lat = -lat

        lon = convert_to_degrees(gps_longitude)
        if gps_longitude_ref != "E":
            lon = -lon

        return lat, lon
    return None


def reverse_geocode(lat, lon):
    """Convert GPS coordinates to a human-readable address."""
    url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
    response = requests.get(url)
    if response.status_code == 200:
        location = response.json()
        return location.get('display_name', 'Address not found')
    return "Unable to retrieve location data"


def analyze_timestamps(exif_data):
    """Check for inconsistencies in timestamp metadata."""
    original = exif_data.get('DateTimeOriginal')
    digitized = exif_data.get('DateTimeDigitized')
    modified = exif_data.get('DateTime')

    st.write("### Timestamp Analysis:")
    st.write(f"**Original DateTime:** {original}")
    st.write(f"**Digitized DateTime:** {digitized}")
    st.write(f"**Modified DateTime:** {modified}")

    if original and modified and original != modified:
        st.warning("The image appears to have been modified after it was originally taken.")


def display_camera_info(exif_data):
    """Display detailed camera and lens information."""
    st.write("### Camera and Lens Information:")
    camera_make = exif_data.get('Make', 'Unknown')
    camera_model = exif_data.get('Model', 'Unknown')
    lens_model = exif_data.get('LensModel', 'Unknown')
    focal_length = exif_data.get('FocalLength', 'Unknown')
    aperture = exif_data.get('ApertureValue', 'Unknown')

    st.write(f"**Camera Make:** {camera_make}")
    st.write(f"**Camera Model:** {camera_model}")
    st.write(f"**Lens Model:** {lens_model}")
    st.write(f"**Focal Length:** {focal_length}")
    st.write(f"**Aperture:** {aperture}")


def compute_file_hash(uploaded_file):
    """Compute and return the SHA-256 hash of the file."""
    hash_sha256 = hashlib.sha256()
    uploaded_file.seek(0)  # Ensure we're at the start of the file
    for chunk in iter(lambda: uploaded_file.read(4096), b""):
        hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def display_file_hash(uploaded_file):
    """Display the file's hash."""
    file_hash = compute_file_hash(uploaded_file)
    st.write("### File Integrity:")
    st.write(f"**SHA-256 Hash:** {file_hash}")


def check_steganography(image):
    """Check for hidden messages using steganography."""
    try:
        hidden_message = lsb.reveal(image)
        if hidden_message:
            st.write("### Steganography:")
            st.warning("Hidden message found in the image!")
            st.write(f"**Hidden Message:** {hidden_message}")
        else:
            st.write("### Steganography:")
            st.write("No hidden messages detected in the image.")
    except IndexError:
        st.write("### Steganography:")
        st.write("No hidden messages detected in the image.")


def export_metadata(exif_data, gps_coordinates, filename="metadata.json"):
    """Export metadata to a downloadable JSON file."""
    metadata = {"EXIF Data": exif_data}
    if gps_coordinates:
        metadata["GPS Coordinates"] = {"Latitude": gps_coordinates[0], "Longitude": gps_coordinates[1]}

    st.download_button(
        label="Download Metadata as JSON",
        data=json.dumps(metadata, indent=4),
        file_name=filename,
        mime="application/json",
    )


def display_exif(exif_data, gps_coordinates):
    """Display EXIF data with reverse geocoded address."""
    st.write("### EXIF Data:")
    for key, value in exif_data.items():
        st.write(f"**{key}:** {value}")

    if gps_coordinates:
        st.write("### GPS Coordinates:")
        lat, lon = gps_coordinates
        st.write(f"**Latitude:** {lat}")
        st.write(f"**Longitude:** {lon}")

        # Reverse geocode to get the address
        address = reverse_geocode(lat, lon)
        st.write(f"**Location:** {address}")

        # Display the location on a map
        st.map(pd.DataFrame([[lat, lon]], columns=['lat', 'lon']))


def main():
    st.title("Advanced EXIF Metadata Extractor")
    st.write("Upload an image to extract its EXIF metadata, perform analysis, and gather additional information.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)

        # Extract EXIF and GPS data
        exif_data, gps_info = get_exif(uploaded_file)

        if exif_data:
            gps_coordinates = get_gps_coordinates(gps_info)
            display_exif(exif_data, gps_coordinates)
            display_camera_info(exif_data)
            analyze_timestamps(exif_data)
            display_file_hash(uploaded_file)
            check_steganography(image)
            export_metadata(exif_data, gps_coordinates)
        else:
            st.write("No EXIF data found in this image.")


if __name__ == "__main__":
    main()
