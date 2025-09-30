from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.product.routes import router as product_router
from app.photo.routes import router as photo_router
from app.customer.routes import router as customer_router
from app.location.routes import router as location_router
from app.linebot_usage.routes import router as linebot_usage_router
from app.db import create_tables
from app.order.routes import router as order_router
from fastapi.staticfiles import StaticFiles

# Create FastAPI application
app = FastAPI(
    title="Backend API",
    description="Backend API for engineering project management",
    version="1.0.0",
    redirect_slashes=False
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
app.include_router(customer_router)
app.include_router(location_router)
app.include_router(order_router)
app.include_router(linebot_usage_router)

# Create database tables
create_tables()
