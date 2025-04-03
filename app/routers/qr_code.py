# Import necessary modules and functions from FastAPI and other standard libraries
from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List
import logging
from pathlib import Path

# Import classes and functions from our application's modules
from app.schema import QRCodeRequest, QRCodeResponse
from app.services.qr_service import generate_qr_code, list_qr_codes, delete_qr_code
from app.utils.common import decode_filename_to_url, encode_url_to_filename
from app.config import settings

# Create an APIRouter instance to register our endpoints
router = APIRouter()

# Setup OAuth2 with Password (and hashing), using a simple OAuth2PasswordBearer scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define an endpoint to create QR codes
# It responds to POST requests at "/" and returns data matching the QRCodeResponse model
# This endpoint is tagged as "QR Codes" in the API docs and returns HTTP 201 when a QR code is created successfully
@router.post("/", response_model=QRCodeResponse, status_code=status.HTTP_201_CREATED, tags=["QR Codes"])
async def create_qr_code(request: QRCodeRequest, token: str = Depends(oauth2_scheme)):
    try:
        # Create QR code directory if it doesn't exist
        settings.QR_DIRECTORY.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from URL
        encoded_url = encode_url_to_filename(str(request.url))
        qr_filename = f"{encoded_url}.png"
        qr_code_path = settings.QR_DIRECTORY / qr_filename
        
        # Generate QR code
        generate_qr_code(
            data=str(request.url),
            path=qr_code_path,
            fill_color=request.fill_color,
            back_color=request.back_color,
            size=request.size
        )
        
        # Generate download URL
        qr_code_download_url = f"{settings.SERVER_BASE_URL}/{settings.SERVER_DOWNLOAD_FOLDER}/{qr_filename}"
        
        # Generate HATEOAS (Hypermedia As The Engine Of Application State) links for this resource
        links = {
            "self": f"{settings.SERVER_BASE_URL}/qr-codes/{qr_filename}",
            "download": qr_code_download_url
        }
        
        # Check if the QR code already exists to prevent duplicates
        if qr_code_path.exists():
            logging.info("QR code already exists.")
            # If it exists, return a conflict response
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "message": "QR code already exists.",
                    "qr_code_url": qr_code_download_url,
                    "links": links
                }
            )

        # Return a response indicating successful creation
        return {
            "message": "QR code created successfully",
            "qr_code_url": qr_code_download_url,
            "links": links
        }
    except Exception as e:
        logging.error(f"Error creating QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Define an endpoint to list all QR codes
# It responds to GET requests at "/" and returns a list of QRCodeResponse objects
@router.get("/", response_model=List[QRCodeResponse], tags=["QR Codes"])
async def list_qr_codes_endpoint(token: str = Depends(oauth2_scheme)):
    try:
        qr_files = list_qr_codes(settings.QR_DIRECTORY)
        responses = []
        
        for qr_file in qr_files:
            url = decode_filename_to_url(qr_file.replace(".png", ""))
            qr_code_download_url = f"{settings.SERVER_BASE_URL}/{settings.SERVER_DOWNLOAD_FOLDER}/{qr_file}"
            
            # Generate HATEOAS (Hypermedia As The Engine Of Application State) links for this resource
            links = {
                "self": f"{settings.SERVER_BASE_URL}/qr-codes/{qr_file}",
                "download": qr_code_download_url
            }
            
            responses.append({
                "message": "QR code found",
                "qr_code_url": qr_code_download_url,
                "links": links
            })
        
        return responses
    except Exception as e:
        logging.error(f"Error listing QR codes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# Define an endpoint to delete a QR code
# It responds to DELETE requests at "/{qr_filename}" and returns HTTP 204 when a QR code is deleted successfully
@router.delete("/{qr_filename}", status_code=status.HTTP_204_NO_CONTENT, tags=["QR Codes"])
async def delete_qr_code_endpoint(qr_filename: str, token: str = Depends(oauth2_scheme)):
    try:
        qr_code_path = settings.QR_DIRECTORY / qr_filename
        if not qr_code_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"QR code {qr_filename} not found"
            )
        
        delete_qr_code(qr_code_path)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error deleting QR code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )