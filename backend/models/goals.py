from sqlalchemy import Column, String, ForeignKey
import uuid
from db.postgres import Base

class Goal(Base):
    __tablename__ = "goals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), index=True)
    goal = Column(String)
    priority = Column(String) # high, medium, low
