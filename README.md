# EUR-Lex Trade Scraper 🇪🇺

A comprehensive web scraper for monitoring EU trade defense regulations from EUR-Lex, specifically targeting antidumping and countervailing duty measures.

## 🎯 Features

### Core Functionality
- **🔍 Smart Web Scraping**: Scrapes EUR-Lex Advanced Search results for trade regulations
- **🎯 Intelligent Keyword Matching**: Advanced matching logic with word boundaries and prefix handling
- **🧹 Duplicate Prevention**: Robust deduplication using document IDs and titles
- **📊 Beautiful Dashboard**: Modern web interface with real-time data visualization
- **🔄 API Integration**: RESTful API for programmatic access

### Keyword Matching Logic
- **Group C (Places/Companies)**: **MANDATORY** - Morocco, ICL, OCP, Nutrien, etc.
- **Groups A & B (Measures/Products)**: **OPTIONAL** - At least one required
  - **Group A**: Trade measures (antidumping, countervailing duty, regulation, etc.)
  - **Group B**: Products (phosphate, fertilizer, DAP, MAP, etc.)

### Advanced Features
- **🎨 Color-coded Keywords**: Visual display of matched keywords in dashboard
- **📅 Current Year Focus**: Optimized for recent trade regulations
- **🔧 CLI Tools**: Command-line interface for automation
- **📈 Export Capabilities**: CSV export with filtering options
- **🌐 Vercel Deployment**: Ready for cloud deployment

## 🚀 **Deployment & Usage**

### **Local Development (Recommended for Full Functionality)**

For complete functionality with persistent data storage:

```bash
# Clone the repository
git clone https://github.com/ARAGRAGMED/eurlex-trade-scraper.git
cd eurlex-trade-scraper

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your EUR-Lex credentials

# Run the scraper
python3 run_scraper.py --force-current-year

# Start the web dashboard
python3 src/main.py
# Open http://localhost:8000
```

**✅ Local Benefits:**
- Persistent data storage in `data/` folder
- Full scraping history maintained
- No data loss between runs
- Complete functionality

### **Vercel Deployment (Limited Functionality)**

The project can be deployed to Vercel, but with **significant limitations**:

**⚠️ Vercel Limitations:**
- Data is stored in `/tmp` directory (temporary)
- Data gets cleared between function invocations
- No persistent storage between requests
- Dashboard shows 0 results after page refresh

**🔧 Vercel Setup:**
```bash
# Deploy to Vercel
vercel --prod

# Environment variables in Vercel dashboard:
EURLEX_USERNAME=your_username
EURLEX_PASSWORD=your_password
```

**📊 Vercel Use Case:**
- Testing the scraper functionality
- Demonstrating the matching logic
- Temporary data viewing
- **NOT suitable for production data collection**

### **Why This Limitation Exists**

Vercel serverless functions:
- Cannot write to persistent file systems
- Only have access to `/tmp` (temporary storage)
- Get cleared between function calls
- Are stateless by design

**💡 Recommendation:** Use Vercel for testing/demo, use local deployment for production data collection.

## 📊 Dashboard Features

### Main Interface
- **📈 KPI Cards**: Total documents, monthly counts, last scrape time, status
- **🔍 Advanced Filters**: Date range, author, company, product, search
- **📋 Interactive Table**: Sortable results with color-coded keywords
- **📊 Charts**: Timeline and document type visualizations

### Keyword Display
- **🛡️ Blue badges**: Trade measures (regulation, dumping, anti-dumping, etc.)
- **🧪 Orange badges**: Products (phosphate, fertilizer, etc.)
- **🌍 Green badges**: Places/Companies (Morocco, ICL, OCP, etc.)

### Actions
- **🔄 Scrape Now**: Trigger immediate scraping with current year focus
- **📥 Export CSV**: Download filtered results
- **👁️ View Details**: Inspect raw document data
- **🔗 External Links**: Direct links to EUR-Lex documents

## 🔧 API Endpoints

### Core Endpoints
```bash
# Trigger scraping
POST /api/scrape?force_current_year=true

# Get dashboard data
GET /api/dashboard-data

# Get specific document
GET /api/documents/{document_id}

# Export CSV
GET /api/export/csv?start_date=2025-01-01&end_date=2025-12-31

# Get filter options
GET /api/authors
GET /api/companies  
GET /api/products
```

### Response Format
```json
{
  "status": "success",
  "message": "Successfully scraped 5 new documents",
  "new_documents": 5,
  "total_documents": 15,
  "duration_seconds": 22.5,
  "from_date": "2025-01-01",
  "to_date": "2025-08-13"
}
```

## 📁 Project Structure

```
eurlex-trade-scraper/
├── src/
│   ├── main.py                 # FastAPI application
│   ├── scraper.py             # Core scraping logic
│   ├── matcher.py             # Keyword matching engine
│   ├── adapters/
│   │   ├── eurlex_web.py      # EUR-Lex web scraping client
│   │   └── eurlex_soap.py     # EUR-Lex SOAP client (legacy)
│   └── web/
│       ├── index.html         # Dashboard UI
│       └── app.js             # Frontend JavaScript
├── data/
│   ├── results-2025.json      # Scraped documents
│   └── state.json             # Application state
├── static/                    # Static web assets
├── api/
│   └── index.py              # Vercel serverless function
├── run_scraper.py            # CLI interface
├── requirements.txt          # Python dependencies
├── vercel.json              # Vercel configuration
└── README.md                # This file
```

## 🎯 Keyword Groups

### Group A: Trade Measures (Optional)
- antidumping, anti-dumping, countervailing duty, CVD
- safeguard, review, sunset review, circumvention
- trade defence, trade defense, sanctions
- regulation, decision, directive

### Group B: Products (Optional)  
- phosphate, phosphate rock, phosphoric acid
- fertilizer, DAP, MAP, TSP, SSP
- HS codes: HS25*, HS31*, 3103, 3105

### Group C: Places/Companies (Mandatory)
- **Countries**: Morocco, Jordan
- **Companies**: ICL, OCP, Mosaic, Nutrien, Yara, Maaden
- **Full names**: Israel Chemicals Limited, Jordan Phosphate Mining Company

## 🔍 Matching Logic

The scraper uses advanced keyword matching with:

### Word Boundary Detection
- ✅ "Morocco" matches in "imports from Morocco"
- ✅ "ICL" matches in "ICL company" 
- ❌ "ICL" does NOT match in "ICLXYZ company"

### Prefix Handling
- ✅ Handles "inMorocco", "fromMorocco", "toMorocco", "ofMorocco"
- ✅ Handles "inICL", "fromICL" patterns

### Matching Requirements
- **Group C (Places/Companies)** must have at least 1 match
- **Groups A or B** must have at least 1 match combined
- Documents matching these criteria are saved and displayed

## 📊 Data Storage

### JSON Format
```json
{
  "TI": "Commission Implementing Regulation (EU) 2025/500...",
  "DN": "32025R0500",
  "DD": "2025-03-13",
  "FM": "Regulation",
  "AU": "European Commission",
  "url": "https://eur-lex.europa.eu/eli/reg/2025/500/oj",
  "scraped_at": "2025-08-13T00:35:06.123456",
  "match_details": {
    "groups_matched": 2,
    "match_score": 3,
    "measure_keywords": ["regulation", "countervailing duty"],
    "product_keywords": [],
    "place_company_keywords": ["Morocco"],
    "matched_snippets": ["...imposing definitive countervailing duties..."]
  }
}
```

### Deduplication
- **Primary**: Document Number (DN/CELEX)
- **Secondary**: Document Title
- **Automatic**: Built into scraping process
- **Manual**: `--clean-duplicates` CLI command

## 🌐 Deployment

### Local Development
```bash
# Start development server
cd src && python3 main.py

# Access at http://localhost:8000
```

### Vercel Deployment
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod

# Configure environment variables in Vercel dashboard
```

### Environment Variables
```bash
# Optional: EUR-Lex SOAP credentials (not required for web scraping)
EURLEX_USERNAME=your_username
EURLEX_PASSWORD=your_password
EURLEX_WSDL_URL=https://eur-lex.europa.eu/EURLexWebService?wsdl
```

## 🔧 Configuration

### Search Parameters
- **Date Range**: Current year by default (`force_current_year=true`)
- **Max Pages**: 10 pages per scrape (configurable)
- **Delay**: 1 second between requests (respectful scraping)

### Keyword Customization
Edit `src/matcher.py` to modify keyword groups:
```python
# Add new companies
self.place_company_keywords.append("NewCompany")

# Add new trade measures  
self.measure_keywords.append("new measure")

# Add new products
self.product_keywords.append("new product")
```

## 🐛 Troubleshooting

### Common Issues

#### No Documents Found
- Check date range (current year has most activity)
- Verify keyword matching logic
- Use `--stats` to see what's in the database

#### Duplicates
- Run `python3 run_scraper.py --clean-duplicates`
- Deduplication is automatic in new scrapes

#### Server Not Starting
- Check if port 8000 is available
- Ensure all dependencies are installed
- Check Python version (3.8+ required)

#### EUR-Lex Connection Issues
- EUR-Lex may have rate limiting
- Try reducing max_pages or increasing delay
- Check EUR-Lex website availability

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python3 run_scraper.py --force-current-year
```

## 📈 Performance

### Metrics
- **Scraping Speed**: ~22 seconds for 10 pages
- **Match Rate**: 100% with current year focus
- **Deduplication**: Automatic and efficient
- **Memory Usage**: Low (streaming JSON processing)

### Optimization
- Current year focus reduces irrelevant documents
- Smart deduplication prevents data bloat
- Efficient keyword matching with compiled regex
- Respectful scraping with delays

## 🤝 Contributing

### Development Setup
```bash
# Fork the repository
git clone <your-fork>
cd eurlex-trade-scraper

# Create feature branch
git checkout -b feature/new-feature

# Make changes and test
python3 run_scraper.py --force-current-year

# Commit and push
git commit -m "Add new feature"
git push origin feature/new-feature
```

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Include type hints where appropriate

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- EUR-Lex for providing public access to EU legal documents
- FastAPI for the excellent web framework
- Tabler for the beautiful UI components
- The open-source community for inspiration and tools

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the API documentation at `/docs`

---

**Built with ❤️ for trade defense monitoring**
