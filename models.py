from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# SQLAlchemy Models
Base = declarative_base()

class ReportDB(Base):
    __tablename__ = "reports"
    
    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    key_findings = Column(Text, nullable=False)  # JSON string
    charts = Column(Text, nullable=False)  # JSON string
    full_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic Models
class ChartDataPoint(BaseModel):
    name: str
    data: Dict[str, Union[str, int, float]] = Field(default_factory=dict)
    
    def __init__(self, **data):
        name = data.pop('name', '')
        remaining_data = {k: v for k, v in data.items() if k != 'name'}
        super().__init__(name=name, data=remaining_data)

class ChartConfig(BaseModel):
    type: str = Field(..., description="Chart type: 'bar', 'line', or 'pie'")
    data: List[Dict[str, Union[str, int, float]]]
    dataKeys: List[Dict[str, str]]
    title: str
    description: str
    xAxisKey: str

class ReportData(BaseModel):
    id: str
    title: str
    summary: str
    keyFindings: List[str]
    charts: List[ChartConfig]
    fullText: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class StoryboardData(BaseModel):
    narrative: str
    charts: List[ChartConfig]

class ChatMessage(BaseModel):
    role: str = Field(..., description="Either 'user' or 'model'")
    content: str
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)

class UploadResponse(BaseModel):
    reports: List[ReportData]
    errors: List[str]
    success_count: int