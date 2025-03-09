from fastapi import FastAPI
from .whatsapp import whatsapp
from .api_routers.webscrape import router as webscrape_router
from fastapi.responses import HTMLResponse
from .rag import rag_routes
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(whatsapp.router)
app.include_router(rag_routes.router)

app.include_router(webscrape_router)


@app.get("/")
async def root():
    content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>API Health Check</title>
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background-color: #f5f5f5;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    color: #333;
                }
                .container {
                    background-color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    padding: 2rem;
                    width: 80%;
                    max-width: 700px;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 0.5rem;
                    text-align: center;
                }
                .status {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: 1.5rem 0;
                }
                .status-indicator {
                    width: 15px;
                    height: 15px;
                    border-radius: 50%;
                    background-color: #2ecc71;
                    margin-right: 10px;
                }
                .info {
                    background-color: #f8f9fa;
                    border-radius: 4px;
                    padding: 1rem;
                    margin: 1rem 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>API Health Status</h1>
                <div class="status">
                    <div class="status-indicator"></div>
                    <span>API is running properly</span>
                </div>
                <div class="info">
                    <p><strong>Environment:</strong> Production</p>
                    <p><strong>Status:</strong> Online</p>
                    <p><strong>Last Check:</strong> <script>document.write(new Date().toLocaleString())</script></p>
                </div>
            </div>
        </body>
    </html>
    """

    return HTMLResponse(content=content,status_code=200)