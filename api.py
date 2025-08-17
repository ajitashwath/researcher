import os
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your modules
from src.create_report.main import ReportCreator
from src.create_report.crew import ReportCrew

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings from environment variables"""
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    serper_api_key: Optional[str] = Field(None, alias="SERPER_API_KEY")
    environment: str = Field("production", alias="ENVIRONMENT")
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    allowed_hosts: List[str] = Field(default_factory=lambda: ["*"])
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

# Global settings instance
settings = Settings()

# Configure logging level based on settings
logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))

# Request/Response Models
class ReportRequest(BaseModel):
    """Request model for report generation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    topic: str = Field(..., min_length=5, max_length=500, description="The topic for the report")
    report_type: str = Field(
        default="Comprehensive Analysis", 
        description="Type of report to generate",
        pattern=r"^(Comprehensive Analysis|Strategic Report|Market Analysis|Technical Report|Business Plan|Research Report)$"
    )
    length: int = Field(
        default=5, 
        ge=1, 
        le=20, 
        description="Approximate number of pages for the report"
    )
    include_charts: bool = Field(
        default=False, 
        description="Whether to include chart suggestions"
    )
    include_sources: bool = Field(
        default=False, 
        description="Whether to include source citations"
    )
    use_crew: bool = Field(
        default=False, 
        description="Use CrewAI for multi-agent report generation"
    )

    @field_validator('topic')
    @classmethod
    def validate_topic(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Topic cannot be empty or whitespace only')
        return v.strip()

class ReportResponse(BaseModel):
    """Response model for report generation"""
    report_id: str
    topic: str
    report_type: str
    content: str
    generated_at: datetime
    word_count: int
    status: str = "completed"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    environment: str
    services: Dict[str, str] = Field(default_factory=dict)

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    timestamp: datetime
    request_id: Optional[str] = None

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger.info("Starting Report Generation API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Log Level: {settings.log_level}")
    
    # Validate API keys
    if not settings.openai_api_key:
        logger.error("OpenAI API key not found in environment variables")
        logger.error("Please set OPENAI_API_KEY environment variable")
        raise RuntimeError("OpenAI API key is required")
    
    logger.info("API keys validated successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Report Generation API...")

# FastAPI app initialization
app = FastAPI(
    title="Report Generation API",
    description="AI-powered comprehensive report generation using OpenAI and CrewAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

if settings.allowed_hosts != ["*"]:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# Dependency to get report creator
def get_report_creator() -> ReportCreator:
    """Dependency to create ReportCreator instance"""
    try:
        return ReportCreator(api_key=settings.openai_api_key)
    except Exception as e:
        logger.error(f"Failed to create ReportCreator: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize report creator: {str(e)}"
        )

# Dependency to get crew report creator
def get_crew_report_creator() -> ReportCrew:
    """Dependency to create ReportCrew instance"""
    try:
        return ReportCrew(api_key=settings.openai_api_key)
    except Exception as e:
        logger.error(f"Failed to create ReportCrew: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize crew report creator: {str(e)}"
        )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message="An unexpected error occurred while processing your request",
            timestamp=datetime.utcnow()
        ).model_dump()
    )

# API Routes
@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Report Generation API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {}
    
    # Check OpenAI API key
    services["openai"] = "configured" if settings.openai_api_key else "not_configured"
    
    # Check Serper API key (optional)
    services["serper"] = "configured" if settings.serper_api_key else "not_configured"
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        environment=settings.environment,
        services=services
    )

@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    report_creator: ReportCreator = Depends(get_report_creator)
):
    """Generate a comprehensive report using the standard approach"""
    try:
        logger.info(f"Generating report for topic: {request.topic}")
        logger.info(f"Report type: {request.report_type}, Length: {request.length} pages")
        
        # Create report configuration
        config = {
            'topic': request.topic,
            'report_type': request.report_type,
            'length': request.length,
            'include_charts': request.include_charts,
            'include_sources': request.include_sources
        }
        
        # Generate report
        report_content = report_creator.create_report(config)
        
        if not report_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate report content"
            )
        
        # Calculate word count
        word_count = len(report_content.split())
        
        # Generate report ID
        report_id = f"RPT_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(request.topic) % 10000:04d}"
        
        # Create response
        response = ReportResponse(
            report_id=report_id,
            topic=request.topic,
            report_type=request.report_type,
            content=report_content,
            generated_at=datetime.utcnow(),
            word_count=word_count,
            metadata={
                "length": request.length,
                "include_charts": request.include_charts,
                "include_sources": request.include_sources,
                "generation_method": "standard"
            }
        )
        
        logger.info(f"Report generated successfully. ID: {report_id}, Word count: {word_count}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )

@app.post("/generate-report-crew", response_model=ReportResponse)
async def generate_report_crew(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    crew_creator: ReportCrew = Depends(get_crew_report_creator)
):
    """Generate a comprehensive report using CrewAI multi-agent approach"""
    try:
        logger.info(f"Generating crew report for topic: {request.topic}")
        logger.info(f"Report type: {request.report_type}, Length: {request.length} pages")
        
        # Create report configuration
        config = {
            'topic': request.topic,
            'report_type': request.report_type,
            'length': request.length,
            'include_charts': request.include_charts,
            'include_sources': request.include_sources
        }
        
        # Generate report using CrewAI
        report_content = crew_creator.generate_report(request.topic, config)
        
        if not report_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate crew report content"
            )
        
        # Calculate word count
        word_count = len(report_content.split())
        
        # Generate report ID
        report_id = f"CREW_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(request.topic) % 10000:04d}"
        
        # Create response
        response = ReportResponse(
            report_id=report_id,
            topic=request.topic,
            report_type=request.report_type,
            content=report_content,
            generated_at=datetime.utcnow(),
            word_count=word_count,
            metadata={
                "length": request.length,
                "include_charts": request.include_charts,
                "include_sources": request.include_sources,
                "generation_method": "crewai"
            }
        )
        
        logger.info(f"Crew report generated successfully. ID: {report_id}, Word count: {word_count}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating crew report: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate crew report: {str(e)}"
        )

@app.post("/generate-report-unified", response_model=ReportResponse)
async def generate_report_unified(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    report_creator: ReportCreator = Depends(get_report_creator),
    crew_creator: ReportCrew = Depends(get_crew_report_creator)
):
    """Generate a report using either standard or CrewAI approach based on request"""
    try:
        logger.info(f"Generating unified report for topic: {request.topic}")
        logger.info(f"Using CrewAI: {request.use_crew}")
        
        # Create report configuration
        config = {
            'topic': request.topic,
            'report_type': request.report_type,
            'length': request.length,
            'include_charts': request.include_charts,
            'include_sources': request.include_sources
        }
        
        # Generate report based on request preference
        if request.use_crew:
            report_content = crew_creator.generate_report(request.topic, config)
            generation_method = "crewai"
            report_prefix = "CREW"
        else:
            report_content = report_creator.create_report(config)
            generation_method = "standard"
            report_prefix = "STD"
        
        if not report_content:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate report content"
            )
        
        # Calculate word count
        word_count = len(report_content.split())
        
        # Generate report ID
        report_id = f"{report_prefix}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(request.topic) % 10000:04d}"
        
        # Create response
        response = ReportResponse(
            report_id=report_id,
            topic=request.topic,
            report_type=request.report_type,
            content=report_content,
            generated_at=datetime.utcnow(),
            word_count=word_count,
            metadata={
                "length": request.length,
                "include_charts": request.include_charts,
                "include_sources": request.include_sources,
                "generation_method": generation_method,
                "use_crew": request.use_crew
            }
        )
        
        logger.info(f"Unified report generated successfully. ID: {report_id}, Method: {generation_method}, Word count: {word_count}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating unified report: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate unified report: {str(e)}"
        )

@app.get("/report-types", response_model=List[str])
async def get_report_types():
    """Get available report types"""
    return [
        "Comprehensive Analysis",
        "Strategic Report", 
        "Market Analysis",
        "Technical Report",
        "Business Plan",
        "Research Report"
    ]

@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """Get API configuration (non-sensitive information only)"""
    return {
        "environment": settings.environment,
        "log_level": settings.log_level,
        "openai_configured": bool(settings.openai_api_key),
        "serper_configured": bool(settings.serper_api_key),
        "supported_report_types": [
            "Comprehensive Analysis",
            "Strategic Report", 
            "Market Analysis",
            "Technical Report",
            "Business Plan",
            "Research Report"
        ],
        "max_report_length": 20,
        "min_report_length": 1
    }

# For testing purposes (development only)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        log_level="info",
        access_log=True
    )