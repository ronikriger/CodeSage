from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
from dotenv import load_dotenv
import json

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
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

class CodeReviewRequest(BaseModel):
    code: str
    language: str
    context: Optional[str] = None

class CodeReviewResponse(BaseModel):
    suggestions: List[str]
    explanation: str
    quality_score: float
    best_practices: List[str]

@app.get("/")
async def root():
    return {"message": "Welcome to CodeSage API"}

@app.post("/api/review", response_model=CodeReviewResponse)
async def review_code(request: CodeReviewRequest):
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
        
        return CodeReviewResponse(
            suggestions=review_data["suggestions"],
            explanation=review_data["explanation"],
            quality_score=review_data["quality_score"],
            best_practices=review_data["best_practices"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 