from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.postgres import SessionLocal
from models.user import User
from utils.security import hash_password, verify_password, create_token
from pydantic import BaseModel
from jose import JWTError, jwt
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if len(request.password) < 6:
        return {"error": "Password too short"}
    user = User(email=request.email, name=request.name, password_hash=hash_password(request.password))
    db.add(user)
    db.commit()
    return {"msg": "User created"}

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        return {"error": "Invalid credentials"}
    
    token = create_token({"sub": user.email})
    return {"token": token}

@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name}

from models.personalization import UserPolicy, PendingReward
from models.system_state import SystemState
from models.evolution import EvolutionSnapshot
from models.mood import MoodLog
from models.behavior import BehaviorLog

@router.post("/reset_learning")
def reset_learning(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(UserPolicy).filter_by(user_id=user.id).delete()
    db.query(PendingReward).filter_by(user_id=user.id).delete()
    db.query(SystemState).filter_by(user_id=user.id).delete()
    db.commit()
    return {"msg": "Adaptive learning matrices have been completely wiped."}

@router.post("/clear_history")
def clear_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db.query(EvolutionSnapshot).filter_by(user_id=user.id).delete()
    db.query(MoodLog).filter_by(user_id=user.id).delete()
    db.query(BehaviorLog).filter_by(user_id=user.id).delete()
    db.commit()
    return {"msg": "All psychological history and behavioral graphs have been wiped."}
