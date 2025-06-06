# 🔍 AI-Powered Lead Recommendation System

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.2+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A full-stack application that combines machine learning with sales automation to prioritize and engage high-quality leads.

## 🌟 Key Features

### 🧠 Intelligent Lead Processing
- **Predictive Scoring**: ML model (Random Forest) generates 0-100 quality scores
- **Real-Time Verification**: Email/Domain validation using Hunter.io API
- **Adaptive Learning**: Incorporates conversion feedback to improve scoring

### 💼 Sales Productivity Tools
- **Smart Filtering and Organisation**: Sort by industry.Get leads arranged by best scores automatically.
- **Bulk Actions**: Export CSV for selected leads of choice or straightaway export verified leads.
- **Template Engine**: Dynamic email personalization (`{name}`, `{company}`)

## 🛠️ Technology Stack

| Component       | Technology          |
|----------------|--------------------|
| Frontend       | Streamlit (Python) |
| Backend API    | FastAPI            |
| Machine Learning | Scikit-learn     |
| Data Processing | Pandas/Numpy     |
| Email Delivery | SMTP (TLS)        |
| Deployment     | Docker            |

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker (optional)

### Local Development
```bash
# Clone the repository
git clone https://github.com/Romit23/Lead-Recommendation-MVP.git
cd Lead-Recommendation-MVP

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Launch services
uvicorn main:app --reload & streamlit run app.py
```

### Docker Deployment
```bash
docker-compose up --build
```
Access:
- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000/docs`

## 📂 Repository Structure
```
Lead-Recommendation-MVP/
├── app/                  # Frontend components
│   ├── app.py            # Streamlit application
│   └── assets/           # Static files
├── backend/              # API components
│   ├── main.py           # FastAPI endpoints
│   ├── lead_scorer.py    # ML model
│   └── hunter_verifier.py # Email verification
├── data/                 # Sample datasets
│   └── leads.csv         # Demo lead data
├── tests/                # Test cases
├── .env          # Environment template
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Container configuration
└── README.md             # This document
```




