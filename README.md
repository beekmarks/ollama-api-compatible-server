# Ollama API-Compatible Server

This project provides an Ollama API-compatible server that uses the `llama-cpp-python` library to run local LLM inference. It allows you to use your own GGUF models with an API that's compatible with Ollama's endpoints, making it easy to integrate with existing tools and applications designed to work with Ollama.

## Features

- **Ollama API Compatibility**: Implements endpoints that match Ollama's API structure
- **Local Inference**: Uses `llama-cpp-python` to run inference on local GGUF model files
- **Model Management**: Implements a model caching system to avoid reloading models
- **Configurable Parameters**: Supports various inference parameters (temperature, max tokens, etc.)

## Requirements

- Python 3.9+ with SSL support
- A GGUF model file (e.g., Llama 3.2)

## Setup Instructions

### Mac

1. **Install Python with SSL support**:
   
   Using Homebrew (recommended):
   ```bash
   brew install python
   ```

   Or download from the [official Python website](https://www.python.org/downloads/macos/).

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install required packages**:
   ```bash
   pip install fastapi uvicorn llama-cpp-python pydantic
   ```

4. **Update the model path**:
   
   Edit the `ollama-api-compatible.py` file and update the `MODEL_PATH` variable to point to your GGUF model file:
   ```python
   MODEL_PATH = "/path/to/your/model.gguf"
   ```

5. **Run the server**:
   ```bash
   python ollama-api-compatible.py
   ```

   The server will run on `http://127.0.0.1:11435` by default.

### Windows

1. **Install Python with SSL support**:
   
   Download and install Python from the [official Python website](https://www.python.org/downloads/windows/).
   
   During installation, make sure to check the box that says "Add Python to PATH".

2. **Create a virtual environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install required packages**:
   ```cmd
   pip install fastapi uvicorn llama-cpp-python pydantic
   ```

4. **Update the model path**:
   
   Edit the `ollama-api-compatible.py` file and update the `MODEL_PATH` variable to point to your GGUF model file:
   ```python
   MODEL_PATH = "C:\\path\\to\\your\\model.gguf"
   ```

5. **Run the server**:
   ```cmd
   python ollama-api-compatible.py
   ```

   The server will run on `http://127.0.0.1:11435` by default.

## API Endpoints

The server implements the following Ollama-compatible endpoints:

- **GET /api/tags**: List available models
- **POST /api/generate**: Generate text completions
- **POST /api/chat**: Handle chat-based interactions
- **GET /api/version**: Get the server version

## Usage Examples

### Checking Available Models

```bash
curl -s http://localhost:11435/api/tags
```

### Generating Text

```bash
curl -s -X POST http://localhost:11435/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "prompt": "Hello, how are you today?",
    "stream": false
  }'
```

### Chat Interaction

```bash
curl -s -X POST http://localhost:11435/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2",
    "messages": [
      {"role": "user", "content": "What are the three laws of robotics?"}
    ],
    "stream": false
  }'
```

## Using in Your Code

### Python Example

```python
import requests
import json

# For text generation
def generate_text(prompt, model="llama3.2"):
    response = requests.post(
        "http://localhost:11435/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

# For chat interaction
def chat(messages, model="llama3.2"):
    response = requests.post(
        "http://localhost:11435/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False
        }
    )
    return response.json()["message"]["content"]

# Example usage
if __name__ == "__main__":
    # Text generation
    result = generate_text("Explain quantum computing in simple terms.")
    print(f"Generated text: {result}")
    
    # Chat interaction
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    result = chat(messages)
    print(f"Chat response: {result}")
```

### JavaScript Example

```javascript
// Using fetch API
async function generateText(prompt, model = "llama3.2") {
  const response = await fetch("http://localhost:11435/api/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: model,
      prompt: prompt,
      stream: false,
    }),
  });
  
  const data = await response.json();
  return data.response;
}

async function chat(messages, model = "llama3.2") {
  const response = await fetch("http://localhost:11435/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: model,
      messages: messages,
      stream: false,
    }),
  });
  
  const data = await response.json();
  return data.message.content;
}

// Example usage
async function example() {
  // Text generation
  const generatedText = await generateText("Write a short poem about coding.");
  console.log("Generated text:", generatedText);
  
  // Chat interaction
  const chatResponse = await chat([
    { role: "user", content: "Explain how to make a sandwich." }
  ]);
  console.log("Chat response:", chatResponse);
}

example();
```

## Advanced Configuration

You can modify the following parameters in the code to customize the server:

- **Port**: Change the port number in the `uvicorn.run()` call
- **Model Parameters**: Adjust the `n_ctx`, `n_gpu_layers`, and other parameters in the `get_or_load_model()` function
- **Response Format**: Customize the response format in the API endpoint handlers

## Troubleshooting

### SSL Issues with pip

If you encounter SSL errors when installing packages with pip, try:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package-name>
```

### Model Loading Errors

- Ensure the model path is correct and the file exists
- Check that you have sufficient RAM to load the model
- For large models, consider enabling GPU acceleration by setting `n_gpu_layers` to a higher value

## License

This project is open source and available under the MIT License.
