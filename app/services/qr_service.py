import os
from typing import List
import qrcode
import logging
from pathlib import Path
from app.config import settings

def list_qr_codes(directory_path: Path) -> List[str]:
    """
    Lists all QR code images in the specified directory by returning their filenames.
    Parameters:
    - directory_path (Path): The filesystem path to the directory containing QR code images.

    Returns:
    - A list of filenames (str) for QR codes found in the directory.
    """
    try:
        # Create directory if it doesn't exist
        directory_path.mkdir(parents=True, exist_ok=True)
        # List all files ending with '.png' in the specified directory.
        return [f for f in os.listdir(directory_path) if f.endswith('.png')]
    except FileNotFoundError:
        logging.error(f"Directory not found: {directory_path}")
        raise
    except OSError as e:
        logging.error(f"An OS error occurred while listing QR codes: {e}")
        raise

def generate_qr_code(data: str, path: Path, fill_color: str = 'black', back_color: str = 'white', size: int = 10):
    """
    Generates a QR code based on the provided data and saves it to a specified file path.
    Parameters:
    - data (str): The data to encode in the QR code.
    - path (Path): The filesystem path where the QR code image will be saved.
    - fill_color (str): Color of the QR code.
    - back_color (str): Background color of the QR code.
    - size (int): The size of each box in the QR code grid.
    """
    logging.debug("QR code generation started")
    try:
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        qr = qrcode.QRCode(version=1, box_size=size, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(str(path))
        logging.info(f"QR code successfully saved to {path}")
    except Exception as e:
        logging.error(f"Failed to generate/save QR code: {e}")
        raise

def delete_qr_code(file_path: Path):
    """
    Deletes the specified QR code image file.
    Parameters:
    - file_path (Path): The filesystem path to the QR code image file to delete.
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logging.info(f"Successfully deleted QR code: {file_path}")
        else:
            logging.warning(f"QR code not found: {file_path}")
            raise FileNotFoundError(f"QR code not found: {file_path}")
    except Exception as e:
        logging.error(f"Failed to delete QR code: {e}")
        raise

def create_directory(directory_path: Path):
    """
    Creates a directory at the specified path if it doesn't already exist.
    Parameters:
    - directory_path (Path): The filesystem path of the directory to create.
    """
    try:
        directory_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Directory created/verified: {directory_path}")
    except Exception as e:
        logging.error(f"Failed to create directory {directory_path}: {e}")
        raise