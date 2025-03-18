# Model File Instructions

This repository does not include the GGUF model files due to their large size. You have several options for obtaining and using model files:

## Option 1: Download from HuggingFace

You can download GGUF model files from HuggingFace repositories such as:
- [TheBloke's Models](https://huggingface.co/TheBloke)
- [Meta's Llama Models](https://huggingface.co/meta-llama)

## Option 2: Convert from Other Formats

If you have models in other formats (like GGML or original PyTorch checkpoints), you can convert them to GGUF using tools like [llama.cpp](https://github.com/ggerganov/llama.cpp).

## Using Your Model

After obtaining a GGUF model file:

1. Place it in the repository directory or any location of your choice
2. Update the `MODEL_PATH` variable in `ollama-api-compatible.py` to point to your model file:

```python
MODEL_PATH = "/path/to/your/model.gguf"  # Update with your model path
```

## Recommended Models

For optimal performance with this server, we recommend:
- Llama 3.2 (8B or 3B Instruct variants)
- Mistral 7B Instruct
- Any GGUF-formatted model compatible with llama.cpp

The quantization level (Q4_K_M, Q5_K_M, etc.) affects the balance between model size and quality. Lower quantization levels (Q2, Q3) result in smaller files but lower quality, while higher levels (Q6, Q8) provide better quality but larger files.
