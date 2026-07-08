from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

# Schemas
class LoginRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"email": "user@example.com", "password": "SecurePass123!"}})

    email: str = Field(description="Kullanıcının e-posta adresi")
    password: str = Field(description="Kullanıcının parolası")

class RegisterRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"email": "user@example.com", "password": "SecurePass123!", "full_name": "John Doe"}})

    email: str = Field(description="Kullanıcının e-posta adresi")
    password: str = Field(description="Kayıt için güçlü parola")
    full_name: str = Field(description="Kullanıcının tam adı")

    def validate_password(self) -> str | None:
        if len(self.password) < 8:
            return "Password must be at least 8 characters"
        if not any(c.isupper() for c in self.password):
            return "Password must contain uppercase letter"
        if not any(c.isdigit() for c in self.password):
            return "Password must contain number"
        return None

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str = Field(description="Kullanıcının e-posta adresi")
    full_name: str | None = Field(default=None, description="Kullanıcının tam adı")

class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default="bearer", description="Token tipi")

# Endpoints
@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """Register new user and return JWT token"""
    # Validate password strength
    pwd_error = req.validate_password()
    if pwd_error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=pwd_error)
    
    # Validate email format
    if "@" not in req.email or "." not in req.email.split("@")[1]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
    
    # Validate name
    if not req.full_name or len(req.full_name.strip()) < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Full name must be at least 2 characters")
    
    # Check if user exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    # Create user
    user = User(
        email=req.email,
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name.strip()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Return token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token}

@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    # Find user
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    # Return token
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token}

@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile"""
    try:
        user_id = int(current_user_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
