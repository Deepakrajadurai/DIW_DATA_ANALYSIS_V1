# German Economic Insights Dashboard

An AI-powered dashboard for analyzing German economic reports, built with Python FastAPI and featuring interactive visualizations, AI-generated narratives, and intelligent chatbot assistance.

![Dashboard Preview](https://via.placeholder.com/800x400/1F2937/FFFFFF?text=German+Economic+Dashboard)

## 🚀 Features

### Core Functionality
- **📊 Interactive Dashboard** - Clean, responsive interface with sidebar navigation
- **📄 PDF Processing** - Upload and automatically extract text from PDF reports
- **🤖 AI Report Generation** - Convert raw text into structured economic reports
- **📈 Dynamic Charts** - Interactive visualizations using Plotly.js
- **📝 AI Narratives** - Generate analytical summaries and insights
- **🔗 Storyboard Synthesis** - Combine multiple reports into macro-economic insights
- **💬 Intelligent Chatbot** - Ask questions about specific reports
- **🗄️ Persistent Storage** - SQLite database with backup functionality

### AI Capabilities
- **Gemini AI Integration** - Advanced natural language processing
- **Automatic Chart Generation** - Extract data and create visualizations
- **Cross-Report Analysis** - Identify connections between different reports
- **Policy Impact Analysis** - Understand economic implications
- **Text-to-Speech** - Audio playback of AI responses

### Technical Features
- **FastAPI Backend** - High-performance Python web framework
- **SQLite Database** - Reliable data persistence with ACID compliance
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Real-time Processing** - Live feedback during file uploads
- **Error Handling** - Comprehensive error reporting and recovery
- **Database Backup** - One-click backup functionality

## 📋 Prerequisites

- **Python 3.8+**
- **Gemini AI API Key** (Get from [Google AI Studio](https://makersuite.google.com/app/apikey))
- **50MB+ available disk space**

## ⚡ Quick Start

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd german_economic_dashboard
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./dashboard.db
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

### 4. Run the Application
```bash
python main.py
```

### 5. Access the Dashboard
Open your browser and navigate to: `http://localhost:8000`

## 📁 Project Structure

```
german_economic_dashboard/
├── main.py                 # FastAPI application entry point
├── models.py              # Pydantic and SQLAlchemy data models
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── dashboard.db          # SQLite database (auto-created)
├── services/             # Business logic layer
│   ├── __init__.py
│   ├── database_service.py    # Database operations
│   ├── gemini_service.py     # AI integration
│   └── pdf_service.py        # PDF text extraction
├── templates/            # HTML templates
│   └── index.html       # Main dashboard page
├── static/              # Static assets
│   ├── app.js          # Frontend JavaScript
│   └── styles.css      # Custom CSS styles
├── data/               # Seed data
│   └── seed_data.py    # Initial database content
└── uploads/            # File upload directory (auto-created)
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini AI API key | - | Yes |
| `DATABASE_URL` | SQLite database URL | `sqlite:///./dashboard.db` | No |
| `DEBUG` | Enable debug mode | `False` | No |
| `HOST` | Server host address | `0.0.0.0` | No |
| `PORT` | Server port number | `8000` | No |

### Application Settings

Edit `config.py` to modify:
- **File Upload Limits** - Maximum PDF file size (default: 50MB)
- **AI Model** - Gemini model version (default: gemini-2.5-flash)
- **Token Limits** - Maximum AI response length (default: 8192)
- **Upload Directory** - File storage location (default: ./uploads)

## 🎯 Usage Guide

### 1. Dashboard Overview
- **Sidebar Navigation** - Access all features from the left panel
- **AI Storyboard** - Generate cross-report analysis
- **Add New Report** - Upload PDF files for processing
- **Economic Reports** - View individual report dashboards

### 2. Uploading Reports
1. Click **"Add New Report"** in the sidebar
2. **Drag & drop** PDF files or **click to browse**
3. **Multiple files** are supported (up to 50MB each)
4. Click **"Analyze PDFs & Generate Dashboards"**
5. Wait for AI processing (may take 1-2 minutes per file)
6. **Automatic redirect** to the first successfully processed report

### 3. Viewing Reports
- **Summary & Key Findings** - Overview of the report
- **Interactive Charts** - Hover and zoom on visualizations
- **AI Narrative** - Click "Generate Analysis" for insights
- **Chatbot** - Ask questions about the specific report
- **Delete Option** - Remove reports you no longer need

### 4. AI Storyboard
- **Cross-Report Analysis** - Synthesizes all reports
- **Macro-Economic Insights** - Identifies broader trends
- **Custom Visualizations** - AI-generated synthesis charts
- **Regenerate Option** - Create new analysis perspectives

### 5. Database Management
- **Statistics** - Click "Stats" in header for database info
- **Backup** - Click "Backup" to save current state
- **Automatic Seeding** - Starts with 5 sample reports

## 🔌 API Endpoints

### Report Management
- `GET /api/reports` - List all reports
- `GET /api/reports/{id}` - Get specific report
- `POST /api/reports/upload` - Upload PDF files
- `DELETE /api/reports/{id}` - Delete report

### AI Features
- `POST /api/generate-narrative/{id}` - Generate analysis
- `POST /api/generate-storyboard` - Create synthesis
- `POST /api/chat/{id}` - Chat with AI about report

### System Operations
- `GET /api/stats` - Database statistics
- `POST /api/backup` - Create database backup
- `GET /` - Main dashboard interface

### Example API Usage
```bash
# List all reports
curl http://localhost:8000/api/reports

# Generate narrative for specific report
curl -X POST http://localhost:8000/api/generate-narrative/construction

# Upload a PDF file
curl -X POST -F "files=@report.pdf" http://localhost:8000/api/reports/upload

# Chat with AI about a report
curl -X POST -F "message=What are the key findings?" http://localhost:8000/api/chat/construction
```

## 🗄️ Database Details

### Storage System
- **Engine**: SQLite 3
- **Location**: `./dashboard.db`
- **Tables**: `reports` (with full CRUD operations)
- **Migrations**: Automatic table creation on first run
- **Backup**: Manual and API-triggered backups

### Data Model
```sql
CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    key_findings TEXT NOT NULL,  -- JSON array
    charts TEXT NOT NULL,        -- JSON array
    full_text TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Sample Data
The database initializes with 5 sample reports:
1. **Construction Industry Crisis** - Decline in nominal construction volume
2. **Women Executives Barometer** - Gender diversity in German companies
3. **Energy Transition in France** - Renewable energy analysis
4. **Sovereign Debt Crises** - 200 years of debt restructuring data
5. **Gender Care Gap** - Informal care work analysis

## 🛠️ Development

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

### Code Structure
- **`main.py`** - FastAPI app, routes, and middleware
- **`models.py`** - Pydantic models and SQLAlchemy schemas
- **`services/`** - Business logic separated by concern
- **`static/app.js`** - Frontend JavaScript (vanilla JS)
- **`templates/index.html`** - Single-page application template

### Adding New Features
1. **Backend**: Add routes to `main.py` and logic to `services/`
2. **Frontend**: Extend `static/app.js` with new functionality
3. **Database**: Update models in `models.py` if needed
4. **AI**: Enhance prompts in `services/gemini_service.py`

### Testing
```bash
# Test API endpoints
curl -X GET http://localhost:8000/api/reports

# Test file upload
curl -X POST -F "files=@test.pdf" http://localhost:8000/api/reports/upload

# Test AI features (requires valid API key)
curl -X POST http://localhost:8000/api/generate-storyboard
```

## 🔍 Troubleshooting

### Common Issues

#### **"AI features are disabled" message**
- **Cause**: Missing or invalid Gemini API key
- **Solution**: Set `GEMINI_API_KEY` in `.env` file
- **Get Key**: Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

#### **PDF text extraction fails**
- **Cause**: PDF is image-based or encrypted
- **Solution**: Use text-based PDFs or OCR preprocessing
- **Alternative**: Copy/paste text into a new document

#### **Database errors**
- **Cause**: Corrupted database or permission issues
- **Solution**: Delete `dashboard.db` (will recreate with sample data)
- **Prevention**: Regular backups via the UI

#### **Upload timeouts**
- **Cause**: Large files or slow AI processing
- **Solution**: Increase timeout or split large documents
- **Workaround**: Upload files one at a time

#### **Charts not displaying**
- **Cause**: Missing Plotly.js or JavaScript errors
- **Solution**: Check browser console and internet connection
- **Alternative**: Refresh page or try different browser

### Performance Optimization
- **File Size**: Keep PDFs under 10MB for faster processing
- **Concurrent Uploads**: Upload 1-2 files at a time
- **Database Size**: Backup and archive old reports periodically
- **Memory Usage**: Restart application if memory usage grows high

### Browser Compatibility
- **Recommended**: Chrome 90+, Firefox 88+, Safari 14+
- **Required Features**: ES6, Fetch API, FormData
- **Mobile**: Responsive design works on iOS and Android

## 📊 Sample Economic Reports

The application comes pre-loaded with 5 sample reports from DIW Berlin:

1. **Construction Industry Analysis** 📏
   - Declining construction volume projections
   - Residential vs. civil engineering trends
   - Interactive bar charts showing sector performance

2. **Women in Executive Leadership** 👩‍💼
   - Gender diversity statistics for top 200 companies
   - Progress tracking from 2022 to 2023
   - "One and done" phenomenon analysis

3. **French Energy Transition** ⚡
   - Nuclear vs. renewable energy mix
   - Heat pump installation progress
   - Policy comparison with Germany

4. **Historical Debt Crises** 💰
   - 200 years of sovereign debt data
   - Serial restructuring analysis
   - Creditor loss patterns

5. **European Care Gap** ❤️
   - Gender inequality in care work
   - Cross-country comparison
   - Policy recommendations

## 🚨 Security Notes

### Data Privacy
- **Local Storage**: All data stored locally in SQLite
- **No Cloud Upload**: PDFs processed locally, not sent to external servers
- **API Key Security**: Gemini API key stored in environment variables
- **File Cleanup**: Uploaded PDFs can be manually deleted

### Production Deployment
```bash
# Set production environment
DEBUG=False
HOST=0.0.0.0
PORT=80

# Use production WSGI server
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Security Checklist
- [ ] Change default database location for production
- [ ] Set up HTTPS with reverse proxy (nginx/Apache)
- [ ] Configure firewall rules for production port
- [ ] Regular database backups
- [ ] Monitor disk usage for uploads directory
- [ ] Validate file types and sizes on upload
- [ ] Rate limiting for API endpoints (optional)

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Test new features locally
- Update documentation for new endpoints

## 📞 Support

### Documentation
- **API Docs**: Available at `http://localhost:8000/docs` when running
- **Interactive API**: Test endpoints at `http://localhost:8000/redoc`

### Issues and Questions
- **GitHub Issues**: Report bugs and request features
- **Email Support**: Contact development team
- **Community**: Join discussions and share feedback

### Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Gemini AI API**: https://ai.google.dev/docs
- **Plotly.js Charts**: https://plotly.com/javascript/
- **SQLAlchemy ORM**: https://docs.sqlalchemy.org/

---

**Built with ❤️ for economic analysis and insights**

*Last updated: December 2024*