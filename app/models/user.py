from sqlalchemy import Column, Integer, String, Date
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False)
    senha = Column(String, nullable=False)

    data_nascimento = Column(Date)

    
   