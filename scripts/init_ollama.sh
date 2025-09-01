#!/bin/bash

# Initialize Ollama with required model
echo "Initializing Ollama with llama3.1:8b model..."

# Wait for Ollama service to be ready
echo "Waiting for Ollama service..."
until curl -f http://localhost:11434/api/version; do
    echo "Ollama not ready, waiting..."
    sleep 5
done

echo "Ollama service is ready!"

echo "Checking if model exists..."
if curl -s http://localhost:11434/api/tags | grep -q "llama3.1:8b"; then
    echo "Model llama3.1:8b already exists, skipping pull..."
else
    echo "Pulling llama3.1:8b model..."
    curl -X POST http://localhost:11434/api/pull \
        -H "Content-Type: application/json" \
        -d '{"name": "llama3.1:8b"}'
fi

echo "Model initialization complete!"

echo "Verifying model is available..."
curl -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{"model": "llama3.1:8b", "prompt": "Test", "stream": false}' \
    | head -c 100

echo -e "\n✅ Ollama initialization complete!"
