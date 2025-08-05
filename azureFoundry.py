import os
import requests
import json
import base64
from pathlib import Path

# --- Configuration - GET THESE FROM AZURE OPENAI ---
# 1. Go to Azure Portal
# 2. Navigate to your Azure OpenAI resource
# 3. Go to "Keys and Endpoint" section
# 4. Copy the endpoint URL and API key
# 5. Make sure you have GPT-4 Vision model deployed

# Set these as environment variables or replace the placeholders directly
# It's highly recommended to use environment variables for keys.
# export AZURE_OPENAI_ENDPOINT="YOUR_ENDPOINT_URL_HERE"
# export AZURE_OPENAI_API_KEY="YOUR_API_KEY_HERE"
# export AZURE_OPENAI_DEPLOYMENT_NAME="YOUR_GPT4_DEPLOYMENT_NAME"

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4-vision")

MODEL_BEING_USED = "GPT-4 Vision (via Azure OpenAI)"

def encode_image(image_path):
    """
    Encode image to base64 string for Azure OpenAI Vision API.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        str: Base64 encoded image string.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def call_azure_openai_gpt4(messages, temperature=0.7, max_tokens=1000):
    """
    Calls GPT-4 Vision model deployed in Azure OpenAI.

    Args:
        messages (list): A list of message objects, e.g.,
                         [{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": [{"type": "text", "text": "What's in this image?"}, 
                                                      {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]}]
        temperature (float): Controls randomness (0.0 to 1.0).
        max_tokens (int): The maximum number of tokens to generate in the completion.

    Returns:
        str: The assistant's response content.

    Raises:
        ValueError: If endpoint URL or API key is not set.
        requests.exceptions.HTTPError: If the API returns an error status.
    """
    if not AZURE_OPENAI_ENDPOINT:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set.")
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable not set.")

    # Construct the full URL for Azure OpenAI
    url = f"{AZURE_OPENAI_ENDPOINT.rstrip('/')}/openai/deployments/{AZURE_OPENAI_DEPLOYMENT_NAME}/chat/completions?api-version=2024-02-15-preview"

    headers = {
        "api-key": AZURE_OPENAI_API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    try:
        print(f"--- Sending request to Azure OpenAI GPT-4 endpoint: {url}")
        print(f"--- Payload (without image data): {json.dumps({k: v for k, v in payload.items() if k != 'messages'}, indent=2)}")

        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()

        response_json = response.json()
        
        if "choices" in response_json and len(response_json["choices"]) > 0:
            first_choice = response_json["choices"][0]
            if "message" in first_choice and "content" in first_choice["message"]:
                return first_choice["message"]["content"].strip()
            else:
                raise ValueError(f"Unexpected response format: 'message.content' not found in choices. Full response: {response_json}")
        else:
            raise ValueError(f"Unexpected response format: 'choices' array not found or empty. Full response: {response_json}")

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
        raise
    except requests.exceptions.Timeout:
        print(f"Request timed out connecting to {url}.")
        raise
    except requests.exceptions.RequestException as req_err:
        print(f"Request exception occurred: {req_err}")
        raise
    except json.JSONDecodeError:
        print(f"Failed to decode JSON response. Status: {response.status_code}")
        print(f"Response content: {response.text}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise

def send_text_message(text_content, system_prompt="You are a helpful assistant."):
    """
    Send a text message to GPT-4.
    
    Args:
        text_content (str): The text message to send.
        system_prompt (str): System prompt for the assistant.
        
    Returns:
        str: The assistant's response.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text_content}
    ]
    
    return call_azure_openai_gpt4(messages)

def send_image_message(image_path, text_prompt="What do you see in this image?", system_prompt="You are a helpful assistant that can analyze images."):
    """
    Send an image with optional text prompt to GPT-4 Vision.
    
    Args:
        image_path (str): Path to the image file.
        text_prompt (str): Text prompt to accompany the image.
        system_prompt (str): System prompt for the assistant.
        
    Returns:
        str: The assistant's response.
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Get file extension to determine MIME type
    file_ext = Path(image_path).suffix.lower()
    mime_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    
    mime_type = mime_type_map.get(file_ext, 'image/jpeg')
    
    # Encode image to base64
    base64_image = encode_image(image_path)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": text_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                }
            ]
        }
    ]
    
    return call_azure_openai_gpt4(messages)

# --- Main Script Execution ---
if __name__ == "__main__":
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        print("Error: Ensure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY environment variables are set.")
        print("Example:")
        print("  export AZURE_OPENAI_ENDPOINT=\"https://your-resource.openai.azure.com\"")
        print("  export AZURE_OPENAI_API_KEY=\"your_api_key_from_azure_portal\"")
        print("  export AZURE_OPENAI_DEPLOYMENT_NAME=\"your_gpt4_deployment_name\"")
        exit(1)

    print(f"Using Azure OpenAI - {MODEL_BEING_USED}")
    print(f"Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Deployment: {AZURE_OPENAI_DEPLOYMENT_NAME}\n")

    # Interactive menu
    print("Choose an option:")
    print("1. Send text message")
    print("2. Send image with prompt")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    try:
        if choice == "1":
            user_question = input("Enter your text message: ")
            print("\nSending text message to GPT-4...")
            response = send_text_message(user_question)
            print("\n--- GPT-4 Response ---")
            print(response)
            
        elif choice == "2":
            image_path = input("Enter path to image file: ").strip()
            text_prompt = input("Enter your prompt about the image (or press Enter for default): ").strip()
            
            if not text_prompt:
                text_prompt = "What do you see in this image?"
                
            print(f"\nSending image and prompt to GPT-4 Vision...")
            response = send_image_message(image_path, text_prompt)
            print("\n--- GPT-4 Vision Response ---")
            print(response)
            
        elif choice == "3":
            print("Goodbye!")
            exit(0)
            
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

    except ValueError as ve:
        print(f"Configuration or Value Error: {ve}")
    except FileNotFoundError as fnf:
        print(f"File Error: {fnf}")
    except requests.exceptions.HTTPError:
        print("Failed to get a successful response from the Azure OpenAI API.")
    except Exception as e:
        print(f"An unhandled error occurred: {e}")