from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
import uvicorn
import logging
from pathlib import Path

from models import ReportData, StoryboardData, UploadResponse
from services.database_service import DatabaseService
from services.gemini_service import GeminiService
from services.pdf_service import PDFService
from config import settings
from data.seed_data import get_seed_data

# Setup logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
# DatabaseService: Handles all database operations
# GeminiService: Handles AI interactions
# PDFService: Handles PDF extraction/validation
db_service = DatabaseService()
gemini_service = GeminiService()
pdf_service = PDFService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """App startup and shutdown logic."""
    # Startup
    logger.info("Starting German Economic Insights Dashboard...")
    db_service.initialize_database()
    
    # Log database stats
    stats = db_service.get_database_stats()
    logger.info(f"Database initialized: {stats}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down German Economic Insights Dashboard...")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="German Economic Insights Dashboard",
    description="AI-powered economic analysis dashboard",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the main dashboard page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/reports")
async def get_reports():
    """Get all reports from the database."""
    try:
        reports = db_service.get_reports()
        return {"reports": [report.dict() for report in reports]}
    except Exception as e:
        logger.error(f"Error fetching reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch reports")

@app.get("/api/reports/{report_id}")
async def get_report(report_id: str):
    """Get a specific report by ID."""
    report = db_service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.dict()

@app.delete("/api/reports/{report_id}")
async def delete_report(report_id: str):
    """Delete a specific report by ID."""
    success = db_service.delete_report(report_id)
    if not success:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}

@app.post("/api/reports/upload")
async def upload_reports(files: List[UploadFile] = File(...)):
    """Upload and process PDF files to create new reports with enhanced error handling."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    new_reports = []
    errors = []
    
    logger.info(f"Processing {len(files)} uploaded files")
    
    for file_index, file in enumerate(files):
        try:
            logger.info(f"Processing file {file_index + 1}/{len(files)}: {file.filename}")
            
            # Validate file properties
            if not file.filename:
                errors.append(f"File {file_index + 1}: No filename provided")
                continue
            
            if not file.filename.lower().endswith('.pdf'):
                errors.append(f"File '{file.filename}': Not a PDF file (only PDF files are supported)")
                continue
            
            # Check file size
            if hasattr(file, 'size') and file.size is not None:
                if file.size == 0:
                    errors.append(f"File '{file.filename}': Empty file")
                    continue
                
                if file.size > settings.MAX_FILE_SIZE:
                    size_mb = file.size / (1024 * 1024)
                    max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
                    errors.append(f"File '{file.filename}': Too large ({size_mb:.1f}MB, max: {max_mb}MB)")
                    continue
                
                logger.info(f"File size: {file.size / (1024 * 1024):.2f}MB")
            
            # Read file content
            try:
                content = await file.read()
                logger.info(f"Successfully read {len(content)} bytes from {file.filename}")
            except Exception as e:
                errors.append(f"File '{file.filename}': Could not read file content - {str(e)}")
                continue
            
            # Validate PDF format
            is_valid, validation_msg = pdf_service.validate_pdf(content)
            if not is_valid:
                errors.append(f"File '{file.filename}': {validation_msg}")
                continue
            
            logger.info(f"PDF validation passed: {validation_msg}")
            
            # Extract text from PDF
            try:
                text = pdf_service.extract_text_from_pdf(content)
                logger.info(f"Text extraction completed. Length: {len(text)} characters")
            except Exception as e:
                errors.append(f"File '{file.filename}': PDF text extraction failed - {str(e)}")
                continue
            
            if not text or not text.strip():
                errors.append(f"File '{file.filename}': No text could be extracted. This might be an image-based PDF or scanned document.")
                continue
            
            # Check if extracted text is meaningful
            if len(text.strip()) < 100:
                errors.append(f"File '{file.filename}': Extracted text too short ({len(text)} characters). Minimum 100 characters required.")
                continue
            
            logger.info(f"Text extraction successful for {file.filename}")
            
            # Generate report using AI
            try:
                logger.info(f"Starting AI processing for {file.filename}")
                report_data = await gemini_service.create_report_from_text(text)
                logger.info(f"AI processing completed for {file.filename}")
                
                # Add detailed logging for AI response validation
                if report_data:
                    logger.info(f"AI successfully generated report: {report_data.id} - {report_data.title}")
                    logger.info(f"Report has {len(report_data.keyFindings)} key findings and {len(report_data.charts)} charts")
                else:
                    logger.error(f"AI returned None for {file.filename} - this indicates the AI could not generate a valid report structure")
                    
            except Exception as e:
                logger.error(f"AI processing failed for {file.filename}: {str(e)}", exc_info=True)
                errors.append(f"File '{file.filename}': AI processing failed - {str(e)}")
                continue
            
            if not report_data:
                logger.error(f"AI returned None for {file.filename} - no structured report could be generated")
                errors.append(f"File '{file.filename}': AI could not generate a structured report from the text")
                continue
            
            # Ensure unique ID
            original_id = report_data.id
            counter = 1
            while db_service.get_report_by_id(report_data.id):
                report_data.id = f"{original_id}_{counter}"
                counter += 1
            
            # Save to database
            try:
                saved_report = db_service.save_report(report_data)
                new_reports.append(saved_report.dict())
                logger.info(f"Successfully processed and saved report: {saved_report.id} from {file.filename}")
            except Exception as e:
                errors.append(f"File '{file.filename}': Database save failed - {str(e)}")
                continue
                
        except Exception as e:
            error_msg = f"File '{file.filename if file.filename else f'file_{file_index + 1}'}': Unexpected error - {str(e)}"
            errors.append(error_msg)
            logger.error(f"Unexpected error processing file: {e}", exc_info=True)
    
    # Log summary
    logger.info(f"Upload processing complete. Success: {len(new_reports)}, Errors: {len(errors)}")
    
    return UploadResponse(
        reports=[ReportData(**report) for report in new_reports],
        errors=errors,
        success_count=len(new_reports)
    ).dict()

@app.post("/api/generate-narrative/{report_id}")
async def generate_narrative(report_id: str):
    """Generate AI narrative for a specific report."""
    report = db_service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        narrative = await gemini_service.generate_narrative(report)
        return {"narrative": narrative}
    except Exception as e:
        logger.error(f"Error generating narrative for {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate narrative")

# main.py - Enhanced error handling
@app.post("/api/generate-storyboard")
async def generate_storyboard():
    """Generate AI storyboard from all reports."""
    try:
        logger.info("Starting storyboard generation")
        
        # Step 1: Get reports
        reports = db_service.get_reports()
        logger.info(f"Retrieved {len(reports) if reports else 0} reports")
        
        if not reports:
            logger.warning("No reports available for storyboard generation")
            raise HTTPException(status_code=400, detail="No reports available for storyboard generation")
        
        # Step 2: Generate storyboard
        logger.info("Calling gemini service for storyboard generation")
        storyboard = await gemini_service.generate_storyboard(reports)
        
        if not storyboard:
            logger.error("Gemini service returned None")
            raise HTTPException(status_code=500, detail="Failed to generate storyboard")
        
        logger.info("Storyboard generated successfully")
        return storyboard.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_storyboard: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate storyboard: {str(e)}")
    
    
@app.post("/api/chat/{report_id}")
async def chat_with_report(report_id: str, message: str = Form(...)):
    """Chat with AI about a specific report."""
    report = db_service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    try:
        response = await gemini_service.chat_with_report(report, message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat for report {report_id}: {e}")
        raise HTTPException(status_code=500, detail="Chat service unavailable")

@app.get("/api/stats")
async def get_database_stats():
    """Get database statistics."""
    try:
        stats = db_service.get_database_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")

@app.post("/api/backup")
async def backup_database():
    """Create a backup of the database."""
    try:
        from datetime import datetime
        backup_path = f"backup_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        db_service.backup_database(backup_path)
        return {"message": f"Database backed up to {backup_path}"}
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail="Failed to create backup")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if AI service is enabled
        ai_status = "enabled" if gemini_service.enabled else "disabled"
        
        # Check database
        db_stats = db_service.get_database_stats()
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "ai_service": ai_status,
            "database": {
                "total_reports": db_stats.get("total_reports", 0),
                "database_size_mb": db_stats.get("database_size_mb", 0)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/timeline")
async def get_highlights_timeline():
    """Get highlights timeline from seed data."""
    try:
        seed_data = get_seed_data()
        # Optionally, add a date field if available in the future
        timeline = [
            {
                "id": report["id"],
                "title": report["title"],
                "summary": report["summary"],
            }
            for report in seed_data
        ]
        return {"timeline": timeline}
    except Exception as e:
        logger.error(f"Error fetching highlights timeline: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch highlights timeline")

@app.post("/api/debug-pdf")
async def debug_pdf_processing(file: UploadFile = File(...)):
    """Debug endpoint to test PDF processing step by step."""
    try:
        logger.info(f"Debug processing file: {file.filename}")
        
        # Read file content
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")
        
        # Validate PDF
        is_valid, validation_msg = pdf_service.validate_pdf(content)
        logger.info(f"PDF validation: {is_valid} - {validation_msg}")
        
        if not is_valid:
            return {"error": f"PDF validation failed: {validation_msg}"}
        
        # Extract text
        text = pdf_service.extract_text_from_pdf(content)
        logger.info(f"Text extraction: {len(text)} characters")
        
        if not text or not text.strip():
            return {"error": "No text could be extracted from PDF"}
        
        if len(text.strip()) < 100:
            return {"error": f"Extracted text too short: {len(text)} characters"}
        
        # Try AI processing
        report_data = await gemini_service.create_report_from_text(text)
        
        if report_data:
            return {
                "success": True,
                "report": {
                    "id": report_data.id,
                    "title": report_data.title,
                    "summary": report_data.summary,
                    "keyFindings": report_data.keyFindings,
                    "charts_count": len(report_data.charts)
                }
            }
        else:
            return {"error": "AI could not generate a structured report"}
            
    except Exception as e:
        logger.error(f"Debug processing error: {e}", exc_info=True)
        return {"error": f"Processing error: {str(e)}"}

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )