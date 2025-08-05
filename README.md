# Azure OpenAI GPT-4 Vision Client

A Python script to interact with GPT-4 Vision model deployed on Azure OpenAI, supporting both text and image inputs.

## Features

- Send text messages to GPT-4
- Analyze images with GPT-4 Vision
- Support for multiple image formats (JPG, PNG, GIF, WebP)
- Interactive command-line interface
- Secure environment variable configuration

## Prerequisites

- Python 3.7+
- Azure OpenAI resource with GPT-4 Vision model deployed
- Required Python packages: `requests`, `python-dotenv` (built-in packages: `os`, `json`, `base64`, `pathlib`)

## Setup

### 1. Install Dependencies

```bash
pip install requests python-dotenv
```

### 2. Configure Azure OpenAI Credentials

Create a `.env` file in the project directory (recommended):

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your actual values
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_KEY=your_api_key_from_azure_portal
AZURE_OPENAI_DEPLOYMENT_NAME=your_gpt4_deployment_name
```

**How to get these values:**
1. Go to Azure Portal
2. Navigate to your Azure OpenAI resource
3. Go to "Keys and Endpoint" section
4. Copy the endpoint URL and API key
5. Deployment name is the name you gave to your GPT-4 model deployment

### 3. Alternative: Environment Variables

You can also set environment variables directly:

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com"
export AZURE_OPENAI_API_KEY="your_api_key_from_azure_portal"
export AZURE_OPENAI_DEPLOYMENT_NAME="your_gpt4_deployment_name"
```

## Usage

### Interactive Mode

Run the script directly:

```bash
python azureFoundry.py
```

Choose from the menu:
- **Option 1**: Send text message to GPT-4
- **Option 2**: Send image with text prompt to GPT-4 Vision
- **Option 3**: Exit

### Programmatic Usage

You can also import and use the functions directly:

```python
from azureFoundry import send_text_message, send_image_message

# Send text message
response = send_text_message("Explain quantum computing in simple terms")
print(response)

# Analyze image
response = send_image_message("path/to/image.jpg", "What objects do you see in this image?")
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