from pydantic import BaseModel, Field, validator
from typing import Dict, Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class QRCodeRequest(BaseModel):
    url: str = Field(..., description="The URL to encode in the QR code")
    fill_color: str = Field(default="black", description="Color of the QR code")
    back_color: str = Field(default="white", description="Background color of the QR code")
    size: int = Field(default=10, ge=1, le=100, description="Size of the QR code (1-100)")

    @validator('fill_color', 'back_color')
    def validate_colors(cls, v):
        allowed_colors = {"black", "white", "red", "green", "blue", "yellow", "purple", "cyan"}
        if v.lower() not in allowed_colors and not v.startswith("#"):
            raise ValueError(f"Color must be one of {allowed_colors} or a hex color code")
        return v.lower()

    @validator('url')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        return v

class QRCodeResponse(BaseModel):
    message: str = Field(..., description="Status message")
    qr_code_url: str = Field(..., description="URL to download the QR code")
    links: Dict[str, str] = Field(..., description="HATEOAS links")

class Link(BaseModel):
    rel: str = Field(..., description="Relation type of the link.")
    href: str = Field(..., description="The URL of the link.")
    action: str = Field(..., description="HTTP method for the action this link represents.")
    type: str = Field(default="application/json", description="Content type of the response for this link.")

    class Config:
        json_schema_extra = {
            "example": {
                "rel": "self",
                "href": "https://api.example.com/qr/123",
                "action": "GET",
                "type": "application/json"
            }
        }