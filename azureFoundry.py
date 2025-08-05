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

def call_azure_ai_llama3(messages, temperature=0.7, max_tokens=500, top_p=0.9):
    """
    Calls a Llama 3 model deployed as a serverless endpoint in Azure AI Studio.

    Args:
        messages (list): A list of message objects, e.g.,
                         [{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": "Explain quantum computing in simple terms."}]
        temperature (float): Controls randomness (0.0 to 1.0).
        max_tokens (int): The maximum number of tokens to generate in the completion.
        top_p (float): Nucleus sampling parameter.

    Returns:
        str: The assistant's response content.

    Raises:
        ValueError: If endpoint URL or API key is not set.
        requests.exceptions.HTTPError: If the API returns an error status.
    """
    if not AZURE_LLAMA_ENDPOINT_URL:
        raise ValueError("AZURE_AI_LLAMA_ENDPOINT_URL environment variable not set.")
    if not AZURE_LLAMA_API_KEY:
        raise ValueError("AZURE_AI_LLAMA_API_KEY environment variable not set.")

    headers = {
        "Authorization": f"Bearer {AZURE_LLAMA_API_KEY}",
        "Content-Type": "application/json",
        # Some Azure MaaS (Models as a Service) endpoints might require this,
        # especially if it's an older AzureML endpoint.
        # Check the "Consume" tab for the exact headers needed.
        # "azureml-model-deployment": "your-deployment-name" # Often the model name itself
    }

    # Payload structure for Llama 3 on Azure typically follows the OpenAI chat completions format.
    # Verify this from the "Consume" or "Test" tab for your specific model endpoint in Azure AI Studio.
    payload = {
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens, # Or sometimes "max_new_tokens" or "max_gen_len"
        # "stream": False, # Set to True for streaming responses
    }

    try:
        print(f"--- Sending request to Azure Llama 3 endpoint: {AZURE_LLAMA_ENDPOINT_URL}")
        print(f"--- Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(AZURE_LLAMA_ENDPOINT_URL, headers=headers, json=payload, timeout=90)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        response_json = response.json()
        print(f"--- API Response: {json.dumps(response_json, indent=2)}")

        # --- IMPORTANT: Adapt this part to match the actual API response structure ---
        # This is a common structure for chat models, but verify with Azure's documentation
        # or by inspecting the actual response from your endpoint.
        if "choices" in response_json and len(response_json["choices"]) > 0:
            first_choice = response_json["choices"][0]
            if "message" in first_choice and "content" in first_choice["message"]:
                return first_choice["message"]["content"].strip()
            # Some models/endpoints might have a slightly different structure
            elif "text" in first_choice: # For older completion models
                return first_choice["text"].strip()
            elif "output" in response_json: # Another possible structure
                 return response_json["output"]
            else:
                raise ValueError(f"Unexpected response format: 'message.content' not found in choices. Full response: {response_json}")
        else:
            # Check for direct output if not in 'choices' (some simpler endpoints might do this)
            if isinstance(response_json, dict) and "output" in response_json:
                 return response_json["output"] # Example, might be different
            elif isinstance(response_json, list) and len(response_json) > 0 and "generated_text" in response_json[0]: # Example HuggingFace style
                return response_json[0]["generated_text"]

            raise ValueError(f"Unexpected response format: 'choices' array not found or empty. Full response: {response_json}")
        # --- End of adaptable response parsing ---

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        print(f"Response content: {response.text}")
        raise
    except requests.exceptions.Timeout:
        print(f"Request timed out connecting to {AZURE_LLAMA_ENDPOINT_URL}.")
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

# --- Main Script Execution ---
if __name__ == "__main__":
    if not AZURE_LLAMA_ENDPOINT_URL or not AZURE_LLAMA_API_KEY:
        print("Error: Ensure AZURE_AI_LLAMA_ENDPOINT_URL and AZURE_AI_LLAMA_API_KEY environment variables are set.")
        print("Example:")
        print("  export AZURE_AI_LLAMA_ENDPOINT_URL=\"https://your-model.region.inference.ai.azure.com/score\"")
        print("  export AZURE_AI_LLAMA_API_KEY=\"your_key_from_azure_ai_studio\"")
        exit(1)

    print(f"Using Azure AI Studio - Llama 3 (or similar) Model: {MODEL_BEING_USED}")
    print(f"Endpoint: {AZURE_LLAMA_ENDPOINT_URL}\n")

    system_prompt = "You are a witty and knowledgeable assistant who loves to explain complex topics with simple analogies."
    user_question = input("Ask Llama something (e.g., 'Why is the sky blue?'): ")

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question},
    ]

    try:
        print("\nSending request to Azure AI Llama endpoint...")
        assistant_response = call_azure_ai_llama3(conversation)
        print("\n--- Llama's Response ---")
        print(assistant_response)

    except ValueError as ve:
        print(f"Configuration or Value Error: {ve}")
    except requests.exceptions.HTTPError:
        print("Failed to get a successful response from the Azure API.")
    except Exception as e:
        print(f"An unhandled error occurred: {e}")