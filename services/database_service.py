import sqlite3
import json
from typing import List, Optional
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import ReportData, ChartConfig, ReportDB, Base
from data.seed_data import get_seed_data
from config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.DATABASE_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=settings.DEBUG)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Create database tables."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def get_db(self) -> Session:
        """Get database session."""
        db = self.SessionLocal()
        try:
            return db
        except Exception as e:
            db.close()
            raise e
    
    def initialize_database(self):
        """Initialize database with seed data if empty."""
        db = self.get_db()
        try:
            # Check if database has any reports
            existing_reports = db.query(ReportDB).count()
            if existing_reports > 0:
                logger.info(f"Database already has {existing_reports} reports")
                return
            
            # Seed with data
            logger.info("Seeding database with initial data...")
            seed_data = get_seed_data()
            
            for report_dict in seed_data:
                report = ReportData(**report_dict)
                self.save_report_with_session(db, report)
            
            db.commit()
            logger.info(f"Database seeded with {len(seed_data)} reports")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            db.close()
    
    def save_report(self, report: ReportData) -> ReportData:
        """Save a report to the database."""
        db = self.get_db()
        try:
            return self.save_report_with_session(db, report)
        finally:
            db.close()
    
    def save_report_with_session(self, db: Session, report: ReportData) -> ReportData:
        """Save a report using existing session."""
        try:
            # Check if report exists
            existing = db.query(ReportDB).filter(ReportDB.id == report.id).first()
            
            if existing:
                # Update existing report
                existing.title = report.title
                existing.summary = report.summary
                existing.key_findings = json.dumps(report.keyFindings)
                existing.charts = json.dumps([chart.dict() for chart in report.charts])
                existing.full_text = report.fullText
                db_report = existing
            else:
                # Create new report
                db_report = ReportDB(
                    id=report.id,
                    title=report.title,
                    summary=report.summary,
                    key_findings=json.dumps(report.keyFindings),
                    charts=json.dumps([chart.dict() for chart in report.charts]),
                    full_text=report.fullText
                )
                db.add(db_report)
            
            db.commit()
            db.refresh(db_report)
            
            # Convert back to Pydantic model
            return self._db_to_pydantic(db_report)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error saving report {report.id}: {e}")
            raise
    
    def get_reports(self) -> List[ReportData]:
        """Get all reports from the database."""
        db = self.get_db()
        try:
            db_reports = db.query(ReportDB).order_by(ReportDB.created_at.desc()).all()
            return [self._db_to_pydantic(db_report) for db_report in db_reports]
        finally:
            db.close()
    
    def get_report_by_id(self, report_id: str) -> Optional[ReportData]:
        """Get a specific report by ID."""
        db = self.get_db()
        try:
            db_report = db.query(ReportDB).filter(ReportDB.id == report_id).first()
            if db_report:
                return self._db_to_pydantic(db_report)
            return None
        finally:
            db.close()
    
    def delete_report(self, report_id: str) -> bool:
        """Delete a report by ID."""
        db = self.get_db()
        try:
            db_report = db.query(ReportDB).filter(ReportDB.id == report_id).first()
            if db_report:
                db.delete(db_report)
                db.commit()
                logger.info(f"Deleted report {report_id}")
                return True
            return False
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting report {report_id}: {e}")
            raise
        finally:
            db.close()
    
    def _db_to_pydantic(self, db_report: ReportDB) -> ReportData:
        """Convert SQLAlchemy model to Pydantic model."""
        return ReportData(
            id=db_report.id,
            title=db_report.title,
            summary=db_report.summary,
            keyFindings=json.loads(db_report.key_findings),
            charts=[ChartConfig(**chart) for chart in json.loads(db_report.charts)],
            fullText=db_report.full_text,
            created_at=db_report.created_at,
            updated_at=db_report.updated_at
        )
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database."""
        import shutil
        try:
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to {backup_path}")
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            raise
    
    def get_database_stats(self) -> dict:
        """Get database statistics."""
        db = self.get_db()
        try:
            total_reports = db.query(ReportDB).count()
            return {
                "total_reports": total_reports,
                "database_path": self.db_path,
                "database_size_mb": Path(self.db_path).stat().st_size / (1024 * 1024) if Path(self.db_path).exists() else 0
            }
        finally:
            db.close()