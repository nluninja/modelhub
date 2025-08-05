# AI Model Hub

Python scripts to interact with various AI models, supporting both text and image inputs.

## Supported Platforms

- **Azure OpenAI**: GPT-4 Vision model
- **Google Vertex AI**: Gemini models with multimodal capabilities

## Features

- Send text messages to AI models
- Analyze images with vision-capable models
- Support for multiple image formats (JPG, PNG, GIF, WebP)
- Interactive command-line interface
- Secure environment variable configuration
- Support for multimodal inputs (text + multiple images)

## Prerequisites

- Python 3.8+
- Access to either:
  - Azure OpenAI resource with GPT-4 Vision model deployed
  - Google Cloud Project with Vertex AI API enabled
- Required Python packages listed in `requirements.txt`

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file in the project directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file with your actual values for the platform(s) you want to use:

#### For Azure OpenAI:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your_api_key_from_azure_portal
AZURE_OPENAI_DEPLOYMENT_NAME=your_gpt4_deployment_name
```

**How to get Azure OpenAI values:**
1. Go to Azure Portal
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the endpoint URL and API key
5. Deployment name is the name you gave to your GPT-4 model deployment

#### For Google Vertex AI:
```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro
```

**How to get Vertex AI values:**
1. Go to Google Cloud Console
2. Create or select a project
3. Enable the Vertex AI API
4. Create a service account with Vertex AI permissions
5. Download the service account key JSON file
6. Set the path to the JSON file in `GOOGLE_APPLICATION_CREDENTIALS`

## Usage

### Azure OpenAI (GPT-4)

Run the Azure OpenAI script:

```bash
python azureFoundry.py
```

Choose from the menu:
- **Option 1**: Send text message to GPT-4
- **Option 2**: Send image with text prompt to GPT-4 Vision
- **Option 3**: Exit

### Google Vertex AI (Gemini)

Run the Vertex AI script:

```bash
python vertex.py
```

Choose from the menu:
- **Option 1**: Send text message to Gemini
- **Option 2**: Send image with text prompt to Gemini Vision
- **Option 3**: Send multimodal message (text + multiple images)
- **Option 4**: Exit

### Programmatic Usage

You can also import and use the functions directly:

#### Azure OpenAI:
```python
from azureFoundry import send_text_message, send_image_message

# Send text message
response = send_text_message("Explain quantum computing in simple terms")
print(response)

# Analyze image
response = send_image_message("path/to/image.jpg", "What objects do you see in this image?")
print(response)
```

#### Google Vertex AI:
```python
from vertex import send_text_message, send_image_message, send_multimodal_message

# Send text message
response = send_text_message("Explain quantum computing in simple terms")
print(response)

# Analyze image
response = send_image_message("path/to/image.jpg", "What objects do you see in this image?")
print(response)

# Send text with multiple images
response = send_multimodal_message("Compare these images", ["image1.jpg", "image2.jpg"])
print(response)
```

## Functions

### `send_text_message(text_content, system_prompt="You are a helpful assistant.")`
- Send a text message to GPT-4
- Returns the assistant's response as a string

### `send_image_message(image_path, text_prompt="What do you see in this image?", system_prompt="You are a helpful assistant that can analyze images.")`
- Send an image with optional text prompt to GPT-4 Vision
- Supports JPG, PNG, GIF, WebP formats
- Returns the assistant's response as a string

### `call_azure_openai_gpt4(messages, temperature=0.7, max_tokens=1000)`
- Low-level function to call Azure OpenAI API directly
- Takes OpenAI-compatible message format

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

## Error Handling

The script includes comprehensive error handling for:
- Missing environment variables
- File not found errors
- HTTP errors from Azure OpenAI API
- JSON parsing errors
- Network timeouts

## Security Notes

- Never commit API keys to version control
- Use environment variables or secure key management systems
- The script uses HTTPS for all API communications
- Image data is base64 encoded for secure transmission

## Troubleshooting

### Common Issues

1. **"Environment variable not set" error**
   - Ensure all required environment variables are set correctly
   - Check for typos in variable names

2. **"HTTP 401 Unauthorized" error**
   - Verify your API key is correct
   - Check that your Azure OpenAI resource is active

3. **"HTTP 404 Not Found" error**
   - Verify your endpoint URL is correct
   - Check that your deployment name matches exactly

4. **"File not found" error**
   - Ensure the image path is correct and accessible
   - Use absolute paths if having issues with relative paths

### API Rate Limits

Azure OpenAI has rate limits. If you encounter 429 errors, wait and retry. Consider implementing exponential backoff for production use.

## License

This project is provided as-is for educational and development purposes.