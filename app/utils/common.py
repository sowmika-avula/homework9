import logging.config
import os
import base64
from typing import List, Dict
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta
from app.config import ADMIN_PASSWORD, ADMIN_USER, ALGORITHM, SECRET_KEY
import validators  # Make sure to install this package
from urllib.parse import urlparse, urlunparse, quote, unquote
import logging

# Load environment variables from .env file for security and configuration.
load_dotenv()

def setup_logging():
    """
    Sets up logging for the application using a configuration file.
    This ensures standardized logging across the entire application.
    """
    # Construct the path to 'logging.conf', assuming it's in the project's root.
    logging_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'logging.conf')
    # Normalize the path to handle any '..' correctly.
    normalized_path = os.path.normpath(logging_config_path)
    # Apply the logging configuration.
    logging.config.fileConfig(normalized_path, disable_existing_loggers=False)

def authenticate_user(username: str, password: str):
    """
    Placeholder for user authentication logic.
    In a real application, replace this with actual authentication against a user database.
    """
    # Simple check against constants for demonstration.
    if username == ADMIN_USER and password == ADMIN_PASSWORD:
        return {"username": username}
    # Log a warning if authentication fails.
    logging.warning(f"Authentication failed for user: {username}")
    return None

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generates a JWT access token. Optionally, an expiration time can be specified.
    """
    # Copy user data and set expiration time for the token.
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    # Encode the data to create the JWT.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def validate_and_sanitize_url(url_str):
    """
    Validates a given URL string and returns a sanitized version if valid.
    Returns None if the URL is invalid, ensuring only safe URLs are processed.
    """
    if validators.url(url_str):
        parsed_url = urlparse(url_str)
        sanitized_url = urlunparse(parsed_url)
        return sanitized_url
    else:
        logging.error(f"Invalid URL provided: {url_str}")
        return None

def encode_url_to_filename(url: str) -> str:
    """
    Encodes a URL into a safe filename format using base64 encoding.
    
    Parameters:
    - url (str): The URL to encode
    
    Returns:
    - str: The encoded filename
    """
    try:
        # URL-encode the string first to handle special characters
        url_encoded = quote(url)
        # Then base64 encode it to make it filename-safe
        encoded = base64.urlsafe_b64encode(url_encoded.encode()).decode()
        return encoded
    except Exception as e:
        logging.error(f"Error encoding URL to filename: {e}")
        raise

def decode_filename_to_url(filename: str) -> str:
    """
    Decodes a filename back to its original URL.
    
    Parameters:
    - filename (str): The encoded filename
    
    Returns:
    - str: The original URL
    """
    try:
        # First base64 decode
        decoded = base64.urlsafe_b64decode(filename.encode()).decode()
        # Then URL-decode
        url = unquote(decoded)
        return url
    except Exception as e:
        logging.error(f"Error decoding filename to URL: {e}")
        raise

def generate_links(action: str, qr_filename: str, base_url: str, download_url: str) -> Dict[str, str]:
    """
    Generates HATEOAS links for QR code resources.
    
    Parameters:
    - action (str): The current action being performed
    - qr_filename (str): The filename of the QR code
    - base_url (str): The base URL of the server
    - download_url (str): The URL where the QR code can be downloaded
    
    Returns:
    - Dict[str, str]: A dictionary of HATEOAS links
    """
    try:
        links = {
            "self": f"{base_url}/qr-codes/{qr_filename}",
            "download": download_url,
            "delete": f"{base_url}/qr-codes/{qr_filename}"
        }
        
        if action == "list":
            links["create"] = f"{base_url}/qr-codes/"
            
        return links
    except Exception as e:
        logging.error(f"Error generating HATEOAS links: {e}")
        raise