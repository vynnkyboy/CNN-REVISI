from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import os
from datetime import datetime
import logging
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import detector
from model_handler import get_detector

# Response models - FIXED
class DetectionResult(BaseModel):
    bbox: List[int]
    class_name: str  # Changed from 'class' to 'class_name'
    confidence: float

class DetectionResponse(BaseModel):
    success: bool
    detections: List[DetectionResult]
    total_count: int
    organic_count: int
    inorganic_count: int
    processing_time: float
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    device: str

# Lifespan context manager (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Waste Detection API...")
    try:
        detector = get_detector()
        logger.info(f"Model loaded successfully on {detector.device}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Waste Detection API...")

# Initialize FastAPI
app = FastAPI(
    title="Waste Detection API",
    description="API for detecting organic and inorganic waste in images",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/", response_model=HealthResponse)
async def root():
    try:
        detector = get_detector()
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            device=str(detector.device)
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            model_loaded=False,
            device="unknown"
        )

@app.get("/health")
async def health_check():
    try:
        detector = get_detector()
        return {
            "status": "ok",
            "model_loaded": True,
            "device": str(detector.device),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Detect waste from uploaded file
@app.post("/detect", response_model=DetectionResponse)
async def detect_waste(
    file: UploadFile = File(..., description="Image file to detect waste")
):
    import time
    start_time = time.time()
    
    try:
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/tiff']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_types)}"
            )
        
        # Read file
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Process detection
        detector = get_detector()
        detections = detector.detect_from_file(contents)
        
        # Calculate statistics
        organic_count = sum(1 for d in detections if d['class_name'] == 'Organik')
        inorganic_count = sum(1 for d in detections if d['class_name'] == 'Anorganik')
        
        processing_time = time.time() - start_time
        
        logger.info(f"Detection completed: {len(detections)} objects found in {processing_time:.2f}s")
        
        return DetectionResponse(
            success=True,
            detections=[DetectionResult(**d) for d in detections],
            total_count=len(detections),
            organic_count=organic_count,
            inorganic_count=inorganic_count,
            processing_time=processing_time,
            message=f"Found {len(detections)} waste items"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

# Detect waste from base64
@app.post("/detect-base64", response_model=DetectionResponse)
async def detect_waste_base64(data: Dict[str, str]):
    import time
    start_time = time.time()
    
    try:
        image_base64 = data.get('image', '')
        if not image_base64:
            raise HTTPException(status_code=400, detail="No image provided")
        
        detector = get_detector()
        detections = detector.detect_from_base64(image_base64)
        
        organic_count = sum(1 for d in detections if d['class_name'] == 'Organik')
        inorganic_count = sum(1 for d in detections if d['class_name'] == 'Anorganik')
        
        processing_time = time.time() - start_time
        
        return DetectionResponse(
            success=True,
            detections=[DetectionResult(**d) for d in detections],
            total_count=len(detections),
            organic_count=organic_count,
            inorganic_count=inorganic_count,
            processing_time=processing_time,
            message=f"Found {len(detections)} waste items"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

# Get model info
@app.get("/model-info")
async def get_model_info():
    try:
        detector = get_detector()
        return {
            "model_type": detector.model_type,
            "device": str(detector.device),
            "classes": detector.classes,
            "input_size": 128,
            "available": True
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )