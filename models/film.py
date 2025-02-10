from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

film_genres = Table(
    "film_genres",
    Base.metadata,
    Column("film_id", Integer, ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
)

class Film(Base):
    __tablename__ = "films"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text)
    image = Column(String)
    video_url = Column(String)
    year = Column(Integer)
    age_limit = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    download_number = Column(Integer, default=0)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)

    user = relationship("User", back_populates="films")
    category = relationship("Category", back_populates="films")
    country = relationship("Country", back_populates="films")
    genres = relationship("Genre", secondary=film_genres, back_populates="films")
