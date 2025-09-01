# app/main.py - FastAPI application with support request processing
from fastapi import FastAPI, HTTPException, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import logging
import os
from datetime import datetime

from .database import get_db, create_tables
from .models import SupportRequest
from .tasks import process_support_request
from .services.ai_classifier import SelfHostedAIClassifier

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Support Request Processing System",
    description="AI-powered support request classification and processing system",
    version="1.0.0",
    docs_url="/docs" if os.getenv('DEBUG', 'false').lower() == 'true' else None,
    redoc_url="/redoc" if os.getenv('DEBUG', 'false').lower() == 'true' else None
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

# Pydantic models for API
class SupportRequestCreate(BaseModel):
    customer_name: str
    email: EmailStr
    subject: str
    description: str

class SupportRequestResponse(BaseModel):
    id: int
    customer_name: str
    email: str
    subject: str
    description: str
    category: Optional[str] = None
    ai_summary: Optional[str] = None
    processing_status: str
    notification_sent: str
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Templates for web interface
templates = Jinja2Templates(directory="templates")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "support-request-processor"
    }

# Web form endpoint
@app.get("/", response_class=HTMLResponse)
async def show_form(request: Request):
    """Display support request form"""
    return templates.TemplateResponse("support_form.html", {"request": request})

# Submit support request via web form
@app.post("/submit", response_class=HTMLResponse)
async def submit_support_request_form(
    request: Request,
    customer_name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle support request submission from web form"""
    try:
        # Create new support request
        support_request = SupportRequest(
            customer_name=customer_name,
            email=email,
            subject=subject,
            description=description,
            processing_status="pending",
            notification_sent="false"
        )
        
        db.add(support_request)
        db.commit()
        db.refresh(support_request)
        
        # Queue for AI processing
        process_support_request.delay(support_request.id)
        
        logger.info(f"Support request {support_request.id} created and queued for processing")
        
        return templates.TemplateResponse("success.html", {
            "request": request,
            "request_id": support_request.id
        })
        
    except Exception as e:
        logger.error(f"Error creating support request: {e}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error": "Failed to submit support request. Please try again."
        })

# API endpoint for creating support requests
@app.post("/api/support-requests", response_model=SupportRequestResponse)
async def create_support_request(
    request_data: SupportRequestCreate,
    db: Session = Depends(get_db)
):
    """Create a new support request via API"""
    try:
        support_request = SupportRequest(
            customer_name=request_data.customer_name,
            email=request_data.email,
            subject=request_data.subject,
            description=request_data.description,
            processing_status="pending",
            notification_sent="false"
        )
        
        db.add(support_request)
        db.commit()
        db.refresh(support_request)
        
        # Queue for AI processing
        process_support_request.delay(support_request.id)
        
        logger.info(f"Support request {support_request.id} created via API")
        
        return support_request
        
    except Exception as e:
        logger.error(f"Error creating support request via API: {e}")
        raise HTTPException(status_code=500, detail="Failed to create support request")

# Get support request by ID
@app.get("/api/support-requests/{request_id}", response_model=SupportRequestResponse)
async def get_support_request(request_id: int, db: Session = Depends(get_db)):
    """Get support request by ID"""
    support_request = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
    
    if not support_request:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    return support_request

# List all support requests
@app.get("/api/support-requests", response_model=List[SupportRequestResponse])
async def list_support_requests(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List support requests with optional filtering"""
    query = db.query(SupportRequest)
    
    if status:
        query = query.filter(SupportRequest.processing_status == status)
    
    requests = query.offset(skip).limit(limit).all()
    return requests

# Admin interface for viewing requests
@app.get("/admin/requests/{request_id}", response_class=HTMLResponse)
async def admin_view_request(request_id: int, request: Request, db: Session = Depends(get_db)):
    """Admin view for individual support request"""
    support_request = db.query(SupportRequest).filter(SupportRequest.id == request_id).first()
    
    if not support_request:
        raise HTTPException(status_code=404, detail="Support request not found")
    
    return templates.TemplateResponse("admin_request.html", {
        "request": request,
        "support_request": support_request
    })

# Statistics endpoint
@app.get("/api/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get processing statistics"""
    total_requests = db.query(SupportRequest).count()
    pending_requests = db.query(SupportRequest).filter(SupportRequest.processing_status == "pending").count()
    processing_requests = db.query(SupportRequest).filter(SupportRequest.processing_status == "processing").count()
    completed_requests = db.query(SupportRequest).filter(SupportRequest.processing_status == "completed").count()
    failed_requests = db.query(SupportRequest).filter(SupportRequest.processing_status == "failed").count()
    
    # Category breakdown
    categories = db.query(SupportRequest.category, db.func.count(SupportRequest.id)).filter(
        SupportRequest.category.isnot(None)
    ).group_by(SupportRequest.category).all()
    
    return {
        "total_requests": total_requests,
        "status_breakdown": {
            "pending": pending_requests,
            "processing": processing_requests,
            "completed": completed_requests,
            "failed": failed_requests
        },
        "category_breakdown": {category: count for category, count in categories},
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/classify")
async def test_ai_classification(
    subject: str = Form(...),
    description: str = Form(...)
):
    """Test AI classification endpoint"""
    try:
        classifier = SelfHostedAIClassifier()
        result = await classifier.classify_request(subject, description)
        
        return {
            "status": "success",
            "classification": result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AI classification test failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/api/ollama/health")
async def check_ollama_health():
    """Check Ollama service health"""
    try:
        classifier = SelfHostedAIClassifier()
        is_healthy = await classifier.check_ollama_health()
        
        return {
            "ollama_healthy": is_healthy,
            "ollama_url": classifier.ollama_url,
            "model": classifier.model,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "ollama_healthy": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
