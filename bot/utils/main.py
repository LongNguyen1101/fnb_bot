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

from bot.core.graph import build_graph
from bot.core.state import BookingState

app = FastAPI(
    title="Restaurant Booking API",
    description="API for managing restaurant table bookings and vector embeddings",
    version="1.0.0",
    docs_url="/docs",  # URL cho Swagger UI (mặc định)
    redoc_url="/redoc"  # URL cho ReDoc (mặc định)
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

@app.get("/")
async def root():
    return {"message": "Welcome to Restaurant Booking API"}

@app.post("/api/v1/chat/", tags=["chat"])
async def chat_with_bot(user_input: str):
    """Xử lý yêu cầu từ người dùng thông qua LangGraph."""
    state = BookingState(
        user_input=user_input,
        greeting_done=False,
        intro_done=False,
        table_id=None,
        customer_id=None,
        branch_id=1,  # Giả định branch_id mặc định
        reservation_date=None,
        reservation_time=None,
        party_size=None,
        customer_name=None,
        customer_phone=None,
        customer_email=None,
        booking_confirmed=False,
        messages=[]
    )

    for event in graph.stream(state):
        if "messages" in event:
            latest_message = event["messages"][-1]["content"]
            return {"response": latest_message}
    
    return {"response": "Có lỗi xảy ra, vui lòng thử lại."}