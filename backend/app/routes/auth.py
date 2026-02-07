from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from app.database import get_db
from app.models import User, Business
from app.auth_utils import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from pydantic import BaseModel

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

# Esquemas Pydantic
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str = "buyer" # buyer, seller

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Dependencia para obtener usuario actual
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si existe
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed_pw = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        hashed_password=hashed_pw,
        full_name=user.full_name,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Si es vendedor, creamos un negocio "dummy" para que pueda empezar
    if user.role == "seller":
        new_business = Business(
            name=f"Negocio de {user.full_name}",
            category="Restaurante",
            address="Dirección pendiente",
            latitude=6.24,
            longitude=-75.56,
            phone="000000",
            owner=new_user
        )
        db.add(new_business)
        db.commit()
        
        # Asignar ID al usuario
        new_user.business_id = new_business.id
        db.commit()

    return new_user

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
