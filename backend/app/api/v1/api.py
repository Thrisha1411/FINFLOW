from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth,
    transactions,
    fraud,
    receipts,
    budgets,
    subscriptions,
    assistant,
    simulator,
    root_cause,
    dashboard,
    audit,
    notifications,
    categories,
    websockets
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Identity"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard Overview"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Payment & Transaction Lifecycle"])
api_router.include_router(fraud.router, prefix="/fraud", tags=["AI Fraud Intelligence"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["Receipt & Invoice Scanner"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["Smart Budgeting & 50/30/20"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscription Management"])
api_router.include_router(assistant.router, prefix="/assistant", tags=["AI Financial Assistant"])
api_router.include_router(simulator.router, prefix="/simulator", tags=["What-If Financial Simulator"])
api_router.include_router(root_cause.router, prefix="/root-cause", tags=["AI Financial Root Cause Analysis"])
api_router.include_router(categories.router, prefix="/categories", tags=["Intelligent Auto-Categorization"])
api_router.include_router(audit.router, prefix="/audit", tags=["Compliance & Audit Trail"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notification Engine"])
api_router.include_router(websockets.router, tags=["Real-Time WebSockets"])
