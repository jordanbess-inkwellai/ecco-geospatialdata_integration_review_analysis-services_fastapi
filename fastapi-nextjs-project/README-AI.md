# AI Features in MCP Server

MCP Server includes optional AI capabilities for data validation, schema matching, and transformation suggestions. These features are controlled by a build flag and can be enabled or disabled as needed.

## Available AI Models

The following AI models are supported:

1. **Jellyfish-13B** (default): A powerful large language model optimized for data understanding and schema matching.
2. **XLNet**: Excels at understanding the context and relationships in sequential data.
3. **T5**: Text-to-Text Transfer Transformer designed for various text transformation tasks.
4. **BERT**: Provides deep bidirectional representations and is excellent for understanding context.

## Enabling AI Features

### Environment Variables

AI features can be enabled and configured using the following environment variables:

- `ENABLE_AI_FEATURES`: Set to "true" to enable AI features (default: "false")
- `AI_MODEL_TYPE`: Select the AI model to use (options: "jellyfish", "xlnet", "t5", "bert", default: "jellyfish")
- `AI_MODEL_DEVICE`: Device to run the model on (options: "cuda", "cpu", default: "cuda" if available, otherwise "cpu")
- `AI_MODEL_QUANTIZATION`: Quantization level for the model (options: "4bit", "8bit", or empty for no quantization, default: "4bit")

### Docker Build

When building the Docker image, you can enable AI features using build arguments:

```bash
docker build -t mcp-server --build-arg ENABLE_AI_FEATURES=true --build-arg AI_MODEL_TYPE=jellyfish .
```

### Docker Compose

The provided `docker-compose.yml` file includes services for each AI model:

- `api`: Base API service without AI features
- `api-jellyfish`: API service with Jellyfish-13B model
- `api-xlnet`: API service with XLNet model
- `api-t5`: API service with T5 model
- `api-bert`: API service with BERT model

To start a specific service:

```bash
# Start the base API service without AI features
docker-compose up api

# Start the API service with Jellyfish-13B model
docker-compose up api-jellyfish

# Start the API service with XLNet model
docker-compose up api-xlnet

# Start the API service with T5 model
docker-compose up api-t5

# Start the API service with BERT model
docker-compose up api-bert
```

## Hardware Requirements

AI models, especially larger ones like Jellyfish-13B, require significant computational resources:

- **Jellyfish-13B**:
  - With 4-bit quantization: ~8GB VRAM
  - With 8-bit quantization: ~16GB VRAM
  - Without quantization: ~26GB VRAM

- **XLNet**, **T5**, **BERT**:
  - With 4-bit quantization: ~2GB VRAM
  - With 8-bit quantization: ~4GB VRAM
  - Without quantization: ~6GB VRAM

If running on CPU, expect significantly slower performance and higher memory usage.

## API Endpoints

When AI features are enabled, the following endpoints become available:

- `GET /api/v1/ai/status`: Get the status of the AI service
- `POST /api/v1/ai/validate-data`: Validate data against a schema or infer data quality issues
- `POST /api/v1/ai/match-schema`: Match source schema to target schema
- `POST /api/v1/ai/suggest-transformations`: Suggest data transformations

## Frontend Integration

When AI features are enabled in the build, the frontend includes:

1. An AI Tools page accessible from the sidebar
2. An AI Models tab in the Settings page
3. AI-specific functionality throughout the application

When AI features are disabled in the build, these UI elements are automatically hidden to provide a clean user experience without AI-related options.

### Environment Variables

The frontend uses the following environment variables to control AI features:

- `NEXT_PUBLIC_AI_ENABLED`: Set to "true" to show AI-related UI elements (default: "false")
- `NEXT_PUBLIC_AI_MODEL`: The default AI model to use (options: "jellyfish", "xlnet", "t5", "bert")

### Docker Compose Configuration

The provided `docker-compose.yml` includes two frontend services:

- `frontend`: Connected to the base API without AI features
- `frontend-jellyfish`: Connected to the API with Jellyfish-13B model enabled

This allows you to run both versions simultaneously for comparison.

## Model Capabilities

Each model has different strengths and capabilities:

### Jellyfish-13B
- Advanced schema matching and data validation
- Detailed data transformation suggestions
- Entity extraction from text fields
- Semantic understanding of data relationships

### XLNet
- Sequential data pattern recognition
- Context-aware data validation
- Advanced text embeddings
- Time series data analysis

### T5
- Text summarization and transformation
- Data format conversion
- Translation between schemas
- Question answering about data

### BERT
- Semantic analysis of text fields
- Sentiment classification
- Named entity recognition
- Context-aware data validation

## Fallback Behavior

If AI features are disabled or if an error occurs during AI processing, the system will fall back to using traditional rule-based methods for data validation, schema matching, and transformation suggestions.
