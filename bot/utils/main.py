# BOOKINGTABLE/bot/utils/main.py
from fastapi import FastAPI
from bot.utils.database import Base, engine, init_vector_schema_and_indexes
from bot.schema.models import *
from bot.schema.vector_models import *
from bot.api.restaurant_routers import restaurant_router
from bot.api.restaurant_branches_routers import restaurant_branches_router
from bot.api.service_type_routers import service_type_router
from bot.api.table_routers import table_router
from bot.api.table_status_routers import table_status_router
from bot.api.reservation_routers import reservation_router
from bot.api.customer_routers import customer_router
from bot.api.policy_type_routers import policy_type_router
from bot.api.policy_routers import policy_router
from bot.api.policy_detail_routers import policy_detail_router
from bot.api.chatbot_router import chatbot_router
from fastapi.middleware.cors import CORSMiddleware

from bot.core.graph import build_graph

app = FastAPI(
    title="Restaurant Booking API",
    description="API for managing restaurant table bookings and vector embeddings",
    version="1.0.0",
    docs_url="/docs",  # URL cho Swagger UI (mặc định)
    redoc_url="/redoc"  # URL cho ReDoc (mặc định)
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific origins (e.g., ["http://localhost:3000"]) in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS
    allow_headers=["Content-Type", "Action"],  # Allow custom Action header
)

graph = build_graph()

# try:
#     # init_vector_schema_and_indexes()
#     Base.metadata.create_all(bind=engine)
#     print("Tables and HNSW indexes created/verified in Supabase.")
# except Exception as e:
#     print(f"Error during initialization: {e}")

app.include_router(restaurant_router, prefix="/api/v1", tags=["restaurant routers"])
app.include_router(restaurant_branches_router, prefix="/api/v1", tags=["restaurant branches routers"])
app.include_router(service_type_router, prefix="/api/v1", tags=["service type routers"])
app.include_router(table_router, prefix="/api/v1", tags=["table routers"])
app.include_router(table_status_router, prefix="/api/v1", tags=["table status routers"])
app.include_router(reservation_router, prefix="/api/v1", tags=["reservation routers"])
app.include_router(customer_router, prefix="/api/v1", tags=["customer routers"])
app.include_router(policy_type_router, prefix="/api/v1", tags=["policy type routers"])
app.include_router(policy_router, prefix="/api/v1", tags=["policy routers"])
app.include_router(policy_detail_router, prefix="/api/v1", tags=["policy detail routers"])
app.include_router(chatbot_router, prefix="/api/v1", tags=["chatbot routers"])

@app.get("/")
async def root():
    return {"message": "Welcome to Restaurant Booking API"}
