# FastAPI Project

A well-structured FastAPI application with organized routes and services.

## Project Structure

```
Predictor/
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py       # Health check endpoints
│   │   └── items.py        # Item CRUD endpoints
│   └── services/
│       ├── __init__.py
│       └── item_service.py # Business logic for items
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
└── venv/                   # Virtual environment
```

## Setup

1. **Create virtual environment** (already done):
   ```bash
   python3 -m venv venv
   ```

2. **Activate virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies** (already done):
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application
python main.py

# Or use uvicorn directly with auto-reload
uvicorn main:app --reload
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive API docs (Swagger)**: http://localhost:8000/docs
- **Alternative API docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health Check
- `GET /health` - Check application health

### Items
- `POST /items/` - Create a new item
- `GET /items/` - Get all items
- `GET /items/{item_id}` - Get a specific item
- `PUT /items/{item_id}` - Update an item
- `DELETE /items/{item_id}` - Delete an item

## Example Usage

### Create an item
```bash
curl -X POST "http://localhost:8000/items/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sample Item",
    "description": "This is a sample item",
    "price": 29.99,
    "tax": 2.50
  }'
```

### Get all items
```bash
curl "http://localhost:8000/items/"
```

### Get a specific item
```bash
curl "http://localhost:8000/items/1"
```

## Architecture

- **Routes** (`api/routes/`): Handle HTTP requests and responses
- **Services** (`api/services/`): Contain business logic and data operations
- **Main** (`main.py`): Application configuration and router registration

This separation of concerns makes the code more maintainable and testable.

