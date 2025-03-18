# ollama-api-compatible.py
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from llama_cpp import Llama
import uvicorn
import logging
import json
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Ollama API Compatible Server")

# Model configuration
MODEL_PATH = "/Users/stephenmccall/Desktop/ollama-server/Llama-3.2-3B-Instruct-Q4_K_M.gguf"  # Updated with actual model path
MODEL_ID = "llama3.2"  # This will be the model ID used in API requests

# Model metadata to simulate Ollama's model info
MODEL_INFO = {
    "license": "llama3",
    "modelfile": "FROM llama3.2\n",
    "parameters": "llama 3.2",
    "template": "{{ .Prompt}}",
    "format": "gguf",
    "family": "llama",
    "families": ["llama"],
    "parameter_size": "8B",
    "quantization_level": "Q4_0"
}

# Global model cache
models = {}

# Define request/response models to match Ollama's API
class GenerateRequest(BaseModel):
    model: str
    prompt: str
    system: Optional[str] = None
    template: Optional[str] = None
    context: Optional[List[int]] = None
    stream: Optional[bool] = False
    raw: Optional[bool] = False
    format: Optional[str] = None
    options: Optional[Dict[str, Any]] = None

class GenerateResponse(BaseModel):
    model: str
    created_at: str
    response: str
    done: bool
    context: Optional[List[int]] = None
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    options: Optional[Dict[str, Any]] = None
    
class ChatResponse(BaseModel):
    model: str
    created_at: str
    message: ChatMessage
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None
    prompt_eval_duration: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration: Optional[int] = None

class ModelInfo(BaseModel):
    name: str
    modified_at: str
    size: int
    digest: str
    details: Dict[str, Any]

class ModelsResponse(BaseModel):
    models: List[ModelInfo]

def get_or_load_model(model_name: str) -> Llama:
    """Get an already loaded model or load it if not available"""
    if model_name in models:
        return models[model_name]
    
    if model_name != MODEL_ID:
        raise HTTPException(status_code=404, detail=f"Model '{model_name}' not found")
    
    try:
        logger.info(f"Loading model {model_name} from {MODEL_PATH}...")
        start_time = time.time()
        
        model = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_gpu_layers=0,  # CPU only, adjust based on your hardware
            verbose=False
        )
        
        load_time = time.time() - start_time
        logger.info(f"Model {model_name} loaded in {load_time:.2f}s")
        
        models[model_name] = model
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

def format_timestamp() -> str:
    """Format current timestamp in RFC3339 format to match Ollama"""
    return time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime())

@app.get("/api/tags", response_model=ModelsResponse)
async def list_models():
    """Simulate Ollama's /api/tags endpoint to list available models"""
    model_size = os.path.getsize(MODEL_PATH) if os.path.exists(MODEL_PATH) else 0
    
    models_list = [
        ModelInfo(
            name=MODEL_ID,
            modified_at=format_timestamp(),
            size=model_size,
            digest="sha256:simulated_digest_value",
            details=MODEL_INFO
        )
    ]
    
    return ModelsResponse(models=models_list)

@app.post("/api/generate")
async def generate(request: GenerateRequest, raw_request: Request):
    """Simulate Ollama's /api/generate endpoint"""
    model_name = request.model
    
    # Get options from request
    options = request.options or {}
    temperature = options.get("temperature", 0.7)
    max_tokens = options.get("num_predict", 512)
    
    # Get model
    model = get_or_load_model(model_name)
    
    # Prepare prompt with system message if provided
    prompt = request.prompt
    if request.system:
        prompt = f"{request.system}\n\n{prompt}"
    
    # Track timing
    start_time = time.time()
    load_duration = 0  # Model is already loaded
    
    # Generate response
    try:
        prompt_start = time.time()
        result = model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["User:", "\n\n"]
        )
        prompt_duration = int((time.time() - prompt_start) * 1000)  # ms
        
        # Extract the generated text
        generated_text = result["choices"][0]["text"].strip()
        
        total_duration = int((time.time() - start_time) * 1000)  # ms
        
        # Stream results if requested
        if request.stream:
            # TODO: Implement streaming for compatibility
            # This is a simplified version without streaming
            pass
        
        # Prepare the response matching Ollama's format
        response = GenerateResponse(
            model=model_name,
            created_at=format_timestamp(),
            response=generated_text,
            done=True,
            total_duration=total_duration,
            load_duration=load_duration,
            prompt_eval_duration=prompt_duration,
            eval_count=len(prompt) + len(generated_text),
            eval_duration=prompt_duration
        )
        
        return response.dict()
    except Exception as e:
        logger.error(f"Error during generation: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Simulate Ollama's /api/chat endpoint"""
    model_name = request.model
    
    # Get options from request
    options = request.options or {}
    temperature = options.get("temperature", 0.7)
    max_tokens = options.get("num_predict", 512)
    
    # Get model
    model = get_or_load_model(model_name)
    
    # Format the conversation history for the model
    prompt = ""
    for msg in request.messages:
        role_prefix = "User: " if msg.role == "user" else "Assistant: "
        prompt += f"{role_prefix}{msg.content}\n"
    
    prompt += "Assistant: "
    
    # Track timing
    start_time = time.time()
    
    # Generate response
    try:
        result = model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["User:", "\n\n"]
        )
        
        # Extract the generated text
        generated_text = result["choices"][0]["text"].strip()
        
        total_duration = int((time.time() - start_time) * 1000)  # ms
        
        # Prepare the response matching Ollama's format
        response = ChatResponse(
            model=model_name,
            created_at=format_timestamp(),
            message=ChatMessage(role="assistant", content=generated_text),
            done=True,
            total_duration=total_duration,
            eval_count=len(prompt) + len(generated_text)
        )
        
        return response.dict()
    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.get("/api/version")
async def version():
    """Return a simulated version for Ollama compatibility"""
    return {"version": "0.1.0", "build": "emulation"}

if __name__ == "__main__":
    uvicorn.run("ollama-api-compatible:app", host="127.0.0.1", port=11435, reload=False)
