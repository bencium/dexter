"""
FastAPI REST API wrapper for Dexter financial research agent.
Provides endpoints for financial analysis queries.
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

from dexter.agent import Agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Dexter Financial Research API",
    description="Autonomous financial research agent that performs deep analysis using task planning and real-time market data",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent
agent = Agent(max_steps=20, max_steps_per_task=5)

# Request/Response Models
class QueryRequest(BaseModel):
    """Request model for financial queries"""
    query: str = Field(
        ...,
        description="Financial research question to analyze",
        example="What was Apple's revenue growth over the last 4 quarters?"
    )
    max_steps: Optional[int] = Field(
        default=20,
        description="Maximum number of steps the agent can take"
    )
    max_steps_per_task: Optional[int] = Field(
        default=5,
        description="Maximum steps per individual task"
    )

class QueryResponse(BaseModel):
    """Response model for financial queries"""
    status: str = Field(description="Status of the query processing")
    query: str = Field(description="Original query")
    answer: Optional[str] = Field(default=None, description="Final answer from agent")
    error: Optional[str] = Field(default=None, description="Error message if any")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    message: str
    api_keys_configured: dict

# API Endpoints

@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Dexter Financial Research API",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/api/health",
            "query": "/api/query (POST)",
            "docs": "/docs"
        }
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint to verify API and dependency status
    """
    from dexter.tools.api import get_provider_status

    openai_key = os.getenv("OPENAI_API_KEY")
    provider_status = get_provider_status()

    api_keys = {
        "openai": "configured" if openai_key else "missing",
        "data_provider": provider_status["provider"],
        "financial_datasets": "configured (optional)" if provider_status["financial_datasets_available"] else "not configured (using yfinance)",
        "yfinance": "available" if provider_status["yfinance_available"] else "not available"
    }

    # Only require OpenAI key for healthy status
    is_healthy = openai_key is not None

    return HealthResponse(
        status="healthy" if is_healthy else "degraded",
        message=f"Using {provider_status['provider']} for financial data" if is_healthy else "OpenAI API key missing",
        api_keys_configured=api_keys
    )

@app.post("/api/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a financial research query using the Dexter agent

    Args:
        request: QueryRequest with the financial question

    Returns:
        QueryResponse with the agent's analysis

    Example:
        ```
        POST /api/query
        {
            "query": "What was Apple's revenue growth over the last 4 quarters?"
        }
        ```
    """
    try:
        logger.info(f"Processing query: {request.query}")

        # Validate API keys (only OpenAI is required now)
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

        # Create agent with custom settings if provided
        query_agent = Agent(
            max_steps=request.max_steps,
            max_steps_per_task=request.max_steps_per_task
        )

        # Run the agent synchronously (agent.run is not async)
        result = query_agent.run(request.query)

        logger.info(f"Query completed successfully")

        return QueryResponse(
            status="success",
            query=request.query,
            answer=result if result else "Analysis completed but no answer generated"
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return QueryResponse(
            status="error",
            query=request.query,
            error=str(e)
        )

@app.get("/api/status")
async def get_status():
    """
    Get current API status and configuration
    """
    return {
        "status": "operational",
        "agent_config": {
            "max_steps": 20,
            "max_steps_per_task": 5
        },
        "available_tools": [
            "get_income_statements",
            "get_balance_sheets",
            "get_cash_flow_statements",
            "get_filings",
            "get_prices",
            "get_financial_metrics"
        ]
    }

# Entry point for uvicorn
def main():
    """Entry point for running the API server"""
    import uvicorn
    uvicorn.run(
        "dexter.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

# For local development
if __name__ == "__main__":
    main()
