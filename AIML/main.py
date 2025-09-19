# main.py
import asyncio
import logging
import random
import sqlite3
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings


# Configuration
class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    app_name: str = "ML Model Serving API"
    debug: bool = True
    db_path: str = "predictions.db"
    log_file: str = "app.log"


# Pydantic models
class PredictionRequest(BaseModel):
    features: List[float]


class PredictionResponse(BaseModel):
    prediction: float


class BackgroundTaskRequest(BaseModel):
    message: str


class TaskResponse(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str


# Custom exceptions
class PredictionError(Exception):
    def __init__(self, message: str):
        self.message = message


# Database dependency
class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the database and create tables"""
        with sqlite3.connect(self.db_path, check_same_thread=False) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    features TEXT NOT NULL,
                    prediction REAL NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path, check_same_thread=False)


# Global instances
settings = Settings()
db_manager = DatabaseManager(settings.db_path)

# Logging configuration
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Dependency injection
def get_db_connection():
    """Dependency to get database connection"""
    conn = db_manager.get_connection()
    try:
        yield conn
    finally:
        conn.close()


def get_settings():
    """Dependency to get settings"""
    return settings


# Background task function
def log_message_task(message: str):
    """Background task to log a message after delay"""
    time.sleep(5)  # 5 second delay
    timestamp = datetime.now().isoformat()
    log_entry = f"{timestamp} - Background Task: {message}\n"
    
    with open("background_tasks.log", "a") as f:
        f.write(log_entry)
    
    logger.info(f"Background task completed: {message}")


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up ML Model Serving API")
    yield
    logger.info("Shutting down ML Model Serving API")


# FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Advanced ML Model Serving API with SQLite database and background tasks",
    version="1.0.0",
    lifespan=lifespan
)


# Custom exception handler
@app.exception_handler(PredictionError)
async def prediction_error_handler(request: Request, exc: PredictionError):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=400,
        content={"error": "Prediction Error", "message": exc.message}
    )


# API Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return HealthResponse(status="ok")


@app.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Prediction endpoint with database logging"""
    try:
        if not request.features:
            raise PredictionError("Features list cannot be empty")
        
        if any(not isinstance(x, (int, float)) for x in request.features):
            raise PredictionError("All features must be numeric")
        
        # Simple prediction: sum of features
        prediction = sum(request.features)
        
        # Log prediction to database
        features_str = ",".join(map(str, request.features))
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (features, prediction) VALUES (?, ?)",
            (features_str, prediction)
        )
        conn.commit()
        
        logger.info(f"Prediction made: {prediction} for features: {request.features}")
        return PredictionResponse(prediction=prediction)
        
    except Exception as e:
        if isinstance(e, PredictionError):
            raise e
        logger.error(f"Unexpected error in prediction: {str(e)}")
        raise PredictionError(f"Prediction failed: {str(e)}")


@app.get("/train")
async def train_model():
    """Simulate model training with random delay"""
    delay = random.randint(5, 20)
    logger.info(f"Starting model training (simulated delay: {delay}s)")
    
    await asyncio.sleep(delay)
    
    logger.info("Model training completed")
    return {"status": "training complete"}


@app.get("/data")
async def get_predictions(conn: sqlite3.Connection = Depends(get_db_connection)):
    """Retrieve all predictions from database"""
    cursor = conn.cursor()
    cursor.execute("SELECT id, features, prediction, timestamp FROM predictions ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    
    predictions = []
    for row in rows:
        predictions.append({
            "id": row[0],
            "features": [float(x) for x in row[1].split(",")],
            "prediction": row[2],
            "timestamp": row[3]
        })
    
    logger.info(f"Retrieved {len(predictions)} predictions from database")
    return predictions


@app.post("/background_task", response_model=TaskResponse)
async def create_background_task(
    request: BackgroundTaskRequest,
    background_tasks: BackgroundTasks
):
    """Create a background task to log a message"""
    background_tasks.add_task(log_message_task, request.message)
    logger.info(f"Background task queued for message: {request.message}")
    return TaskResponse(status="task started")


# Web UI endpoint
@app.get("/", response_class=HTMLResponse)
async def get_web_ui():
    """Serve the web UI"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ML Model Serving API</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            
            .header {
                background: linear-gradient(135deg, #2196F3, #21CBF3);
                color: white;
                padding: 40px;
                text-align: center;
            }
            
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                font-weight: 300;
            }
            
            .header p {
                font-size: 1.2em;
                opacity: 0.9;
            }
            
            .content {
                padding: 40px;
            }
            
            .endpoint-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .endpoint-card {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                border-left: 4px solid;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                min-height: 140px;
                display: flex;
                flex-direction: column;
            }
            
            .endpoint-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 30px rgba(0,0,0,0.1);
            }
            
            .endpoint-card.get { border-left-color: #28a745; }
            .endpoint-card.post { border-left-color: #007bff; }
            
            .endpoint-card h3 {
                color: #333;
                margin-bottom: 10px;
                font-size: 1.1em;
                flex-shrink: 0;
            }
            
            .method {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: bold;
                margin-bottom: 10px;
                text-transform: uppercase;
            }
            
            .method.get {
                background: #28a745;
                color: white;
            }
            
            .method.post {
                background: #007bff;
                color: white;
            }
            
            .endpoint-card p {
                color: #666;
                line-height: 1.5;
                margin-bottom: 10px;
                font-size: 0.9em;
                flex-grow: 1;
            }
            
            .test-section {
                background: #f8f9fa;
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 30px;
            }
            
            .test-section h3 {
                color: #333;
                margin-bottom: 20px;
            }
            
            .test-form {
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            
            .form-group {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            label {
                font-weight: 500;
                color: #555;
            }
            
            input, textarea, select {
                padding: 12px 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s ease;
            }
            
            input:focus, textarea:focus, select:focus {
                outline: none;
                border-color: #007bff;
            }
            
            button {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 8px;
                font-size: 1em;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            button:hover {
                background: linear-gradient(135deg, #0056b3, #004085);
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,123,255,0.4);
            }
            
            .response {
                background: #f8f9fa;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 15px;
                margin-top: 15px;
                font-family: 'Courier New', monospace;
                white-space: pre-wrap;
                max-height: 300px;
                overflow-y: auto;
            }
            
            .response.success {
                border-color: #28a745;
                background: #d4edda;
            }
            
            .response.error {
                border-color: #dc3545;
                background: #f8d7da;
            }
            
            .loading {
                opacity: 0.6;
                pointer-events: none;
            }
            
            @media (max-width: 768px) {
                .endpoint-grid {
                    grid-template-columns: 1fr;
                    gap: 15px;
                }
                
                .header h1 {
                    font-size: 2em;
                }
                
                .content {
                    padding: 20px;
                }
                
                .endpoint-card {
                    min-height: auto;
                }
            }
            
            @media (min-width: 1400px) {
                .endpoint-grid {
                    grid-template-columns: repeat(5, 1fr);
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 ML Model Serving API</h1>
                <p>Advanced FastAPI application with SQLite database and background tasks</p>
            </div>
            
            <div class="content">
                <h2 style="margin-bottom: 30px; color: #333;">Available Endpoints</h2>
                
                <div class="endpoint-grid">
                    <div class="endpoint-card get">
                        <span class="method get">GET</span>
                        <h3>/health</h3>
                        <p>Health check endpoint that returns the API status.</p>
                    </div>
                    
                    <div class="endpoint-card post">
                        <span class="method post">POST</span>
                        <h3>/predict</h3>
                        <p>Make predictions by sending a list of features. Logs results to database.</p>
                    </div>
                    
                    <div class="endpoint-card get">
                        <span class="method get">GET</span>
                        <h3>/train</h3>
                        <p>Simulate model training with a random delay between 5-20 seconds.</p>
                    </div>
                    
                    <div class="endpoint-card get">
                        <span class="method get">GET</span>
                        <h3>/data</h3>
                        <p>Retrieve all prediction records from the SQLite database.</p>
                    </div>
                    
                    <div class="endpoint-card post">
                        <span class="method post">POST</span>
                        <h3>/background_task</h3>
                        <p>Create a background task that logs a message after 5 seconds.</p>
                    </div>
                </div>
                
                <h2 style="margin-bottom: 30px; color: #333;">Test Endpoints</h2>
                
                <!-- Health Check -->
                <div class="test-section">
                    <h3>🟢 Health Check</h3>
                    <button onclick="testHealth()">Check Health</button>
                    <div id="health-response" class="response" style="display: none;"></div>
                </div>
                
                <!-- Predict -->
                <div class="test-section">
                    <h3>🔮 Make Prediction</h3>
                    <div class="test-form">
                        <div class="form-group">
                            <label for="features">Features (comma-separated numbers):</label>
                            <input type="text" id="features" placeholder="1.5, 2.3, 4.1, 0.8" value="1.5, 2.3, 4.1, 0.8">
                        </div>
                        <button onclick="testPredict()">Make Prediction</button>
                    </div>
                    <div id="predict-response" class="response" style="display: none;"></div>
                </div>
                
                <!-- Train -->
                <div class="test-section">
                    <h3>🎯 Train Model</h3>
                    <button onclick="testTrain()">Start Training</button>
                    <div id="train-response" class="response" style="display: none;"></div>
                </div>
                
                <!-- Data -->
                <div class="test-section">
                    <h3>📊 Get Predictions Data</h3>
                    <button onclick="testData()">Get All Predictions</button>
                    <div id="data-response" class="response" style="display: none;"></div>
                </div>
                
                <!-- Background Task -->
                <div class="test-section">
                    <h3>⚙️ Background Task</h3>
                    <div class="test-form">
                        <div class="form-group">
                            <label for="message">Message:</label>
                            <input type="text" id="message" placeholder="Hello from background task!" value="Hello from background task!">
                        </div>
                        <button onclick="testBackgroundTask()">Start Background Task</button>
                    </div>
                    <div id="bg-response" class="response" style="display: none;"></div>
                </div>
            </div>
        </div>
        
        <script>
            async function makeRequest(url, method = 'GET', body = null) {
                const options = {
                    method,
                    headers: {
                        'Content-Type': 'application/json',
                    }
                };
                
                if (body) {
                    options.body = JSON.stringify(body);
                }
                
                try {
                    const response = await fetch(url, options);
                    const data = await response.json();
                    return { success: response.ok, data, status: response.status };
                } catch (error) {
                    return { success: false, data: { error: error.message }, status: 0 };
                }
            }
            
            function displayResponse(elementId, response) {
                const element = document.getElementById(elementId);
                element.style.display = 'block';
                element.textContent = JSON.stringify(response.data, null, 2);
                element.className = `response ${response.success ? 'success' : 'error'}`;
            }
            
            async function testHealth() {
                const response = await makeRequest('/health');
                displayResponse('health-response', response);
            }
            
            async function testPredict() {
                const featuresInput = document.getElementById('features').value;
                const features = featuresInput.split(',').map(x => parseFloat(x.trim()));
                
                if (features.some(isNaN)) {
                    displayResponse('predict-response', {
                        success: false,
                        data: { error: 'Invalid features. Please enter comma-separated numbers.' }
                    });
                    return;
                }
                
                const response = await makeRequest('/predict', 'POST', { features });
                displayResponse('predict-response', response);
            }
            
            async function testTrain() {
                const button = event.target;
                const originalText = button.textContent;
                button.textContent = 'Training...';
                button.disabled = true;
                
                const response = await makeRequest('/train');
                displayResponse('train-response', response);
                
                button.textContent = originalText;
                button.disabled = false;
            }
            
            async function testData() {
                const response = await makeRequest('/data');
                displayResponse('data-response', response);
            }
            
            async function testBackgroundTask() {
                const message = document.getElementById('message').value;
                const response = await makeRequest('/background_task', 'POST', { message });
                displayResponse('bg-response', response);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )