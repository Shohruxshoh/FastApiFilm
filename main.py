from fastapi import FastAPI
from routes import user, category, country, genre, film
from models.database import engine, Base
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.include_router(user.router, prefix='/auth')
app.include_router(category.router, prefix='/categories')
app.include_router(country.router, prefix='/countries')
app.include_router(genre.router, prefix='/genres')
app.include_router(film.router, prefix='/films')


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# Ma'lumotlar bazasini yaratish
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def on_startup():
    await create_tables()


@app.get('/')
async def home():
    return {"message": "Salom"}