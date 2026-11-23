from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserRegister(UserBase):
    password: str = Field(min_length=8)
    org_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    totp_code: Optional[str] = None

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_totp_enabled: bool
    role: str
    organization_id: Optional[str]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class TOTPSetupResponse(BaseModel):
    secret: str
    provisioning_uri: str
    recovery_codes: List[str]

class TOTPVerifyRequest(BaseModel):
    code: str
