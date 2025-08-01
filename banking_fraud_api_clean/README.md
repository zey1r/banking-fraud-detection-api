# Banking Fraud Detection API

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Enterprise-grade fraud detection API for banking applications with ML capabilities.

## Features

- 🔒 **Enterprise Security**: PCI DSS, BDDK, ISO 27001 compliant
- 🤖 **Machine Learning**: XGBoost, LightGBM ensemble models
- 📊 **Real-time Detection**: Sub-second fraud scoring
- 🔍 **Audit Trail**: Tamper-proof logging for compliance
- 🚀 **High Performance**: Async FastAPI with optimized ML pipeline

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/zey1r/banking-fraud-detection-api.git
cd banking-fraud-detection-api

# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev,ml]"
```

### Running the API

```bash
# Development server
uvicorn src.banking_fraud_api.api.main:app --reload

# Production server
uvicorn src.banking_fraud_api.api.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up -d
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/banking_fraud_api

# Run specific test file
pytest tests/test_fraud_detection.py
```

## Project Structure

```
banking_fraud_api_clean/
├── src/
│   └── banking_fraud_api/
│       ├── api/              # FastAPI routes
│       ├── core/             # Configuration, security
│       ├── models/           # Data models, ML models
│       ├── services/         # Business logic
│       ├── repositories/     # Data access layer
│       └── utils/            # Utilities
├── tests/                    # Test suite
├── docs/                     # Documentation
├── scripts/                  # Deployment scripts
└── pyproject.toml           # Project configuration
```

## Environment Variables

Create `.env` file:

```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=postgresql://user:pass@localhost/fraud_db
LOG_LEVEL=INFO
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email dev@verivigil.com or create an issue.
