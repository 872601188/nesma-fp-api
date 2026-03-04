# NESMA Function Point API

A comprehensive API and web application for calculating NESMA (Netherlands Software Metrics Association) function points from software requirements.

## Features

- **Automatic Analysis**: Analyze software requirements text to identify function point components
- **File Upload Support**: Upload requirement documents for analysis
- **Excel Export**: Generate detailed Excel reports of function point calculations
- **Web Interface**: User-friendly React frontend for easy interaction
- **RESTful API**: Full-featured FastAPI backend with comprehensive endpoints

## What are Function Points?

Function Point Analysis (FPA) is a standardized method for measuring the functional size of software. The NESMA method identifies five types of components:

### Data Functions
- **ILF (Internal Logical File)**: Data stored within the application boundary (7-15 FP)
- **EIF (External Interface File)**: Data referenced from external applications (5-10 FP)

### Transactional Functions
- **EI (External Input)**: Processes data entering the application (3-6 FP)
- **EO (External Output)**: Processes data exiting the application with calculations (4-7 FP)
- **EQ (External Inquiry)**: Processes data retrieval without calculations (3-6 FP)

## Project Structure

```
nesma-fp-api/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── Dockerfile             # Container configuration
│   └── nesma/
│       ├── analyzer.py        # Requirement analysis engine
│       ├── calculator.py      # Function point calculator
│       └── excel_generator.py # Excel report generator
├── frontend/
│   ├── package.json           # Node.js dependencies
│   └── src/
│       └── App.js             # React application
├── .github/workflows/
│   └── deploy.yml             # CI/CD pipeline
└── README.md                  # This file
```

## Quick Start

### Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

The web interface will be available at `http://localhost:3000`

### Docker

```bash
cd backend
docker build -t nesma-fp-api .
docker run -p 8000:8000 nesma-fp-api
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/analyze` | POST | Analyze requirements text |
| `/analyze-file` | POST | Upload and analyze file |
| `/export-excel` | POST | Export results to Excel |
| `/nesma/complexity-table` | GET | Get complexity weights |
| `/nesma/gsc-factors` | GET | Get GSC factors |

### Example API Usage

```bash
# Analyze requirements
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The system shall allow users to create customer records. Users can search for customers and generate monthly reports.",
    "project_name": "Customer Management System"
  }'
```

## NESMA Calculation Method

### Complexity Weights

| Component | Low | Average | High |
|-----------|-----|---------|------|
| ILF | 7 | 10 | 15 |
| EIF | 5 | 7 | 10 |
| EI | 3 | 4 | 6 |
| EO | 4 | 5 | 7 |
| EQ | 3 | 4 | 6 |

### Value Adjustment Factor (VAF)

The VAF is calculated using 14 General System Characteristics (GSC):

```
VAF = 0.65 + (Σ GSC values) / 100
```

Each GSC is rated from 0 (not present) to 5 (strong influence).

### Adjusted Function Points

```
Adjusted FP = Unadjusted FP × VAF
```

## Deployment

The project includes a GitHub Actions workflow for CI/CD. Configure the deployment steps in `.github/workflows/deploy.yml` based on your hosting platform (AWS, Azure, Heroku, etc.).

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Resources

- [NESMA Official Website](https://nesma.nl)
- [Function Point Counting Practices Manual](https://www.ifpug.org)
- [ISO/IEC 20926:2009](https://www.iso.org/standard/40474.html)

## Contact

For questions or support, please open an issue on GitHub.
