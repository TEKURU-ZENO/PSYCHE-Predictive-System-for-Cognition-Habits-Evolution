from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.postgres import SessionLocal
from models.user import User
from models.personalization import UserPolicy, PendingReward
from models.system_state import SystemState
from models.agent_metrics import AgentMetrics
from services.privacy_vault import PrivacyVaultService
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


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    email_clean = request.email.strip().lower()
    if "@" not in email_clean or "." not in email_clean:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a valid email address.")
    if len(request.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters.")
    if db.query(User).filter(User.email == email_clean).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")

    user = User(email=email_clean, name=request.name.strip() or email_clean.split("@")[0], password_hash=hash_password(request.password))
    db.add(user)
    db.commit()
    return {"msg": "User created"}


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    email_clean = request.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_token({"sub": user.email})
    return {"token": token, "token_type": "bearer"}


@router.post("/demo")
def demo_login(db: Session = Depends(get_db)):
    """Provides instant verified demo session token for friction-free exploration."""
    demo_email = "demo@psychai.com"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        user = User(
            email=demo_email,
            name="Alex Mercer (Demo)",
            password_hash=hash_password("demopassword123")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    token = create_token({"sub": user.email})
    return {"token": token, "email": user.email, "name": user.name}


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name}


@router.post("/reset_learning")
def reset_learning(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    uid = str(user.id)
    db.query(UserPolicy).filter_by(user_id=uid).delete()
    db.query(PendingReward).filter_by(user_id=uid).delete()
    db.query(SystemState).filter_by(user_id=uid).delete()
    db.query(AgentMetrics).filter_by(user_id=uid).delete()
    db.commit()
    return {"msg": "Adaptive learning matrices have been completely wiped."}


@router.post("/clear_history")
def clear_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    counts = PrivacyVaultService.erase_all_user_data(db, user.id)
    return {"msg": "All psychological history and behavioral graphs have been wiped.", "deleted_counts": counts}


@router.delete("/account")
def delete_account(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    counts = PrivacyVaultService.erase_all_user_data(db, user.id)
    db.query(User).filter(User.id == user.id).delete()
    db.commit()
    return {"msg": "Account and all associated cognitive twin records permanently erased.", "deleted_counts": counts}
