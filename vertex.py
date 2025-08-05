import os
import json
import base64
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using system environment variables only.")
    print("Install with: pip install python-dotenv")

try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    import vertexai
    from vertexai.generative_models import GenerativeModel, Part
except ImportError:
    print("Error: Google Cloud Vertex AI SDK not installed.")
    print("Install with: pip install google-cloud-aiplatform")
    exit(1)

# --- Configuration - GET THESE FROM GOOGLE CLOUD ---
# 1. Go to Google Cloud Console
# 2. Create or select a project
# 3. Enable the Vertex AI API
# 4. Create a service account and download the key file
# 5. Set up authentication

# Create a .env file in the project directory with:
# GOOGLE_CLOUD_PROJECT=your-project-id
# GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
# VERTEX_AI_LOCATION=us-central1  # For GDPR compliance, use: europe-west1
# VERTEX_AI_MODEL=gemini-1.5-pro
# 
# For GDPR compliance, use EU regions like:
# VERTEX_AI_LOCATION=europe-west1  # Belgium (recommended for GDPR)
# VERTEX_AI_LOCATION=europe-west3  # Frankfurt, Germany
# VERTEX_AI_LOCATION=europe-west4  # Netherlands

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
VERTEX_AI_LOCATION = os.getenv("VERTEX_AI_LOCATION", "us-central1")
VERTEX_AI_MODEL = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-pro")

MODEL_BEING_USED = f"Google Vertex AI - {VERTEX_AI_MODEL}"

def initialize_vertex_ai():
    """Initialize Vertex AI with credentials and project settings."""
    try:
        if GOOGLE_APPLICATION_CREDENTIALS and Path(GOOGLE_APPLICATION_CREDENTIALS).exists():
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_APPLICATION_CREDENTIALS
            )
            vertexai.init(
                project=GOOGLE_CLOUD_PROJECT,
                location=VERTEX_AI_LOCATION,
                credentials=credentials
            )
        else:
            # Try using default credentials (useful in GCP environments)
            vertexai.init(
                project=GOOGLE_CLOUD_PROJECT,
                location=VERTEX_AI_LOCATION
            )
        
        return True
    except Exception as e:
        print(f"Failed to initialize Vertex AI: {e}")
        return False

def encode_image_for_vertex(image_path):
    """
    Encode image to base64 for Vertex AI.
    
    Args:
        image_path (str): Path to the image file.
        
    Returns:
        Part: Vertex AI Part object containing the image.
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # Get MIME type based on file extension
    file_ext = Path(image_path).suffix.lower()
    mime_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    
    mime_type = mime_type_map.get(file_ext, 'image/jpeg')
    
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
    
    return Part.from_data(data=image_data, mime_type=mime_type)

def call_vertex_ai(content_parts, generation_config=None):
    """
    Call Vertex AI Generative Model.
    
    Args:
        content_parts (list): List of content parts (text and/or images).
        generation_config (dict, optional): Generation configuration parameters.
        
    Returns:
        str: The model's response text.
    """
    if not initialize_vertex_ai():
        raise RuntimeError("Failed to initialize Vertex AI")
    
    try:
        model = GenerativeModel(VERTEX_AI_MODEL)
        
        # Default generation config
        if generation_config is None:
            generation_config = {
                "max_output_tokens": 2048,
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40
            }
        
        print(f"--- Sending request to Vertex AI model: {VERTEX_AI_MODEL}")
        print(f"--- Generation config: {json.dumps(generation_config, indent=2)}")
        
        response = model.generate_content(
            content_parts,
            generation_config=generation_config
        )
        
        if response.text:
            return response.text.strip()
        else:
            # Handle safety filters or other response issues
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason'):
                    raise ValueError(f"Generation stopped due to: {candidate.finish_reason}")
            raise ValueError("No text generated in response")
            
    except Exception as e:
        print(f"Error calling Vertex AI: {e}")
        raise

def send_text_message(text_content, system_instruction="You are a helpful assistant."):
    """
    Send a text message to Vertex AI.
    
    Args:
        text_content (str): The text message to send.
        system_instruction (str): System instruction for the model.
        
    Returns:
        str: The model's response.
    """
    # Combine system instruction with user content
    full_prompt = f"System: {system_instruction}\n\nUser: {text_content}"
    
    content_parts = [full_prompt]
    return call_vertex_ai(content_parts)

def send_image_message(image_path, text_prompt="What do you see in this image?", system_instruction="You are a helpful assistant that can analyze images."):
    """
    Send an image with text prompt to Vertex AI Vision.
    
    Args:
        image_path (str): Path to the image file.
        text_prompt (str): Text prompt to accompany the image.
        system_instruction (str): System instruction for the model.
        
    Returns:
        str: The model's response.
    """
    image_part = encode_image_for_vertex(image_path)
    
    # Combine system instruction with user prompt
    full_prompt = f"System: {system_instruction}\n\nUser: {text_prompt}"
    
    content_parts = [full_prompt, image_part]
    return call_vertex_ai(content_parts)

def send_multimodal_message(text_content, image_paths=None, system_instruction="You are a helpful assistant."):
    """
    Send a multimodal message with text and multiple images to Vertex AI.
    
    Args:
        text_content (str): The text content.
        image_paths (list, optional): List of paths to image files.
        system_instruction (str): System instruction for the model.
        
    Returns:
        str: The model's response.
    """
    full_prompt = f"System: {system_instruction}\n\nUser: {text_content}"
    content_parts = [full_prompt]
    
    if image_paths:
        for image_path in image_paths:
            image_part = encode_image_for_vertex(image_path)
            content_parts.append(image_part)
    
    return call_vertex_ai(content_parts)

# --- Main Script Execution ---
if __name__ == "__main__":
    if not GOOGLE_CLOUD_PROJECT:
        print("Error: GOOGLE_CLOUD_PROJECT environment variable not set.")
        print("Example configuration:")
        print("  export GOOGLE_CLOUD_PROJECT=\"your-project-id\"")
        print("  export GOOGLE_APPLICATION_CREDENTIALS=\"path/to/service-account-key.json\"")
        print("  export VERTEX_AI_LOCATION=\"us-central1\"")
        print("  export VERTEX_AI_MODEL=\"gemini-1.5-pro\"")
        exit(1)

    print(f"Using {MODEL_BEING_USED}")
    print(f"Project: {GOOGLE_CLOUD_PROJECT}")
    print(f"Location: {VERTEX_AI_LOCATION}\n")

    # Interactive menu
    print("Choose an option:")
    print("1. Send text message")
    print("2. Send image with prompt")
    print("3. Send multimodal message (text + multiple images)")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    try:
        if choice == "1":
            user_question = input("Enter your text message: ")
            print(f"\nSending text message to {VERTEX_AI_MODEL}...")
            response = send_text_message(user_question)
            print(f"\n--- {VERTEX_AI_MODEL} Response ---")
            print(response)
            
        elif choice == "2":
            image_path = input("Enter path to image file: ").strip()
            text_prompt = input("Enter your prompt about the image (or press Enter for default): ").strip()
            
            if not text_prompt:
                text_prompt = "What do you see in this image?"
                
            print(f"\nSending image and prompt to {VERTEX_AI_MODEL}...")
            response = send_image_message(image_path, text_prompt)
            print(f"\n--- {VERTEX_AI_MODEL} Response ---")
            print(response)
            
        elif choice == "3":
            text_content = input("Enter your text message: ")
            
            image_paths = []
            while True:
                image_path = input("Enter path to image file (or press Enter to finish): ").strip()
                if not image_path:
                    break
                if Path(image_path).exists():
                    image_paths.append(image_path)
                else:
                    print(f"Warning: Image file not found: {image_path}")
            
            if not image_paths:
                print("No valid image paths provided. Sending as text-only message.")
                response = send_text_message(text_content)
            else:
                print(f"\nSending multimodal message to {VERTEX_AI_MODEL}...")
                response = send_multimodal_message(text_content, image_paths)
            
            print(f"\n--- {VERTEX_AI_MODEL} Response ---")
            print(response)
            
        elif choice == "4":
            print("Goodbye!")
            exit(0)
            
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

    except ValueError as ve:
        print(f"Configuration or Value Error: {ve}")
    except FileNotFoundError as fnf:
        print(f"File Error: {fnf}")
    except RuntimeError as re:
        print(f"Runtime Error: {re}")
    except Exception as e:
        print(f"An unhandled error occurred: {e}")