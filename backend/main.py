from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import openai
import os
from dotenv import load_dotenv
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from . import models, auth
from .database import SessionLocal, engine
import uuid

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CodeSage API",
    description="AI-powered code review assistant API",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]

    async def broadcast(self, message: str, exclude: str = None):
        for client_id, connection in self.active_connections.items():
            if client_id != exclude:
                await connection.send_text(message)

manager = ConnectionManager()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class CodeReviewRequest(BaseModel):
    code: str
    language: str
    context: Optional[str] = None

class CodeReviewResponse(BaseModel):
    suggestions: List[str]
    explanation: str
    quality_score: float
    best_practices: List[str]

class SharedSnippetCreate(BaseModel):
    code: str
    language: str
    title: str
    description: Optional[str] = None
    is_public: bool = True

# Authentication endpoints
@app.post("/api/auth/register", response_model=Token)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth.create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Code review endpoints
@app.post("/api/review", response_model=CodeReviewResponse)
async def review_code(
    request: CodeReviewRequest,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        # Prepare the prompt for OpenAI
        prompt = f"""Analyze the following {request.language} code and provide a detailed review:
        
        Code:
        {request.code}
        
        Context: {request.context if request.context else 'No additional context provided'}
        
        Please provide:
        1. Code suggestions for improvement
        2. A clear explanation of the code
        3. A quality score (0-100)
        4. Best practices recommendations
        
        Format the response as JSON with the following structure:
        {{
            "suggestions": ["suggestion1", "suggestion2", ...],
            "explanation": "detailed explanation",
            "quality_score": 85.5,
            "best_practices": ["practice1", "practice2", ...]
        }}
        """

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert code reviewer. Provide detailed, constructive feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        # Parse the response
        review_data = json.loads(response.choices[0].message.content)
        
        # Save the review to database
        db_review = models.CodeReview(
            user_id=current_user.id,
            code=request.code,
            language=request.language,
            review_data=json.dumps(review_data)
        )
        db.add(db_review)
        db.commit()
        
        return CodeReviewResponse(
            suggestions=review_data["suggestions"],
            explanation=review_data["explanation"],
            quality_score=review_data["quality_score"],
            best_practices=review_data["best_practices"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint for real-time collaboration
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client {client_id}: {data}", exclude=client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client {client_id} left the chat")

# Shared snippets endpoints
@app.post("/api/snippets")
async def create_snippet(
    snippet: SharedSnippetCreate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    db_snippet = models.SharedSnippet(
        user_id=current_user.id,
        code=snippet.code,
        language=snippet.language,
        title=snippet.title,
        description=snippet.description,
        is_public=snippet.is_public
    )
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)
    return db_snippet

@app.get("/api/snippets")
async def get_snippets(
    skip: int = 0,
    limit: int = 10,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    snippets = db.query(models.SharedSnippet).filter(
        (models.SharedSnippet.is_public == True) |
        (models.SharedSnippet.user_id == current_user.id)
    ).offset(skip).limit(limit).all()
    return snippets

@app.get("/api/snippets/{snippet_id}")
async def get_snippet(
    snippet_id: str,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    snippet = db.query(models.SharedSnippet).filter(models.SharedSnippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    if not snippet.is_public and snippet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this snippet")
    return snippet

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 