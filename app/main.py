from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.product.routes import router as product_router
from app.photo.routes import router as photo_router
from app.db import create_tables
from fastapi.staticfiles import StaticFiles

# Create FastAPI application
app = FastAPI(
    title="Backend API",
    description="Backend API for engineering project management",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="/app/app/uploads"), name="static")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(product_router)
app.include_router(photo_router)

# Create database tables
create_tables()
