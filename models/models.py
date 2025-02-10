# from datetime import datetime
# from typing import List
# from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Table
# from sqlalchemy.orm import relationship, declarative_base
# from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker

# DATABASE_URL = "postgresql+asyncpg://username:password@localhost/dbname"  # PostgreSQL ulanish URL'ni o'zgartiring

# engine = create_async_engine(DATABASE_URL, echo=True)
# async_session = async_sessionmaker(engine, expire_on_commit=False)

# Base = declarative_base()

# # Many-to-Many relationship for Film and Genre
# film_genres = Table(
#     "film_genres",
#     Base.metadata,
#     Column("film_id", Integer, ForeignKey("films.id", ondelete="CASCADE"), primary_key=True),
#     Column("genre_id", Integer, ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True),
# )


# class User(Base, AsyncAttrs):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, nullable=False, unique=True)
#     phone = Column(String, nullable=False, unique=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

#     films = relationship("Film", back_populates="user")


# class Category(Base, AsyncAttrs):
#     __tablename__ = "categories"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)

#     films = relationship("Film", back_populates="category")


# class Genre(Base, AsyncAttrs):
#     __tablename__ = "genres"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)

#     films = relationship("Film", secondary=film_genres, back_populates="genres")


# class Country(Base, AsyncAttrs):
#     __tablename__ = "countries"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False, unique=True)

#     films = relationship("Film", back_populates="country")


# class Film(Base, AsyncAttrs):
#     __tablename__ = "films"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     body = Column(Text)
#     image = Column(String)
#     video_url = Column(String)
#     year = Column(Integer)
#     age_limit = Column(Integer)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     download_number = Column(Integer, default=0)

#     user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
#     category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
#     country_id = Column(Integer, ForeignKey("countries.id", ondelete="SET NULL"), nullable=True)

#     user = relationship("User", back_populates="films")
#     category = relationship("Category", back_populates="films")
#     country = relationship("Country", back_populates="films")
#     genres = relationship("Genre", secondary=film_genres, back_populates="films")


# async def init_db():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
