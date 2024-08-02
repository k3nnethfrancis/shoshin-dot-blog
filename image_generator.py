import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from PIL import Image
import requests
from io import BytesIO
import re

# Load environment variables
load_dotenv()

# Initialize clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_image_prompt(post_content):
    """Generate an image prompt using Claude."""
    system_prompt = (
        "You are an AI assistant tasked with creating image prompts for blog posts. "
        "Given the content of a blog post, create a concise and vivid prompt for "
        "an image that captures the essence of the post. The prompt should be "
        "suitable for an AI image generation model like DALL-E. "
        "Styles we like are glitch, pixel art, and retro, bladerunner, and cyberpunk, trippy, and renaissance surreal."
    )
    
    response = anthropic_client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=100,
        system=system_prompt,
        messages=[
            {"role": "user", "content": f"Create an image prompt for this blog post:\n\n{post_content}"}
        ]
    )
    return response.content[0].text.strip()

def generate_and_save_image(prompt, filename):
    """Generate an image using DALL-E, crop it, and save it."""
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    
    # Download the image
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # Calculate the crop dimensions
    width, height = img.size
    new_height = height // 3
    top = (height - new_height) // 2
    bottom = top + new_height
    
    # Crop the image
    cropped_img = img.crop((0, top, width, bottom))
    
    # Ensure the directory exists
    os.makedirs("assets/img", exist_ok=True)
    
    # Save the cropped image
    img_path = f"assets/img/{filename}.png"
    cropped_img.save(img_path)
    
    print(f"Image saved: {img_path}")  # Add this line for debugging
    return img_path

def sanitize_filename(filename):
    """Sanitize the filename to be safe for file systems."""
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def generate_post_image(post_content, post_title):
    """Main function to generate and save an image for a blog post."""
    prompt = generate_image_prompt(post_content)
    sanitized_title = sanitize_filename(post_title)
    img_path = generate_and_save_image(prompt, sanitized_title)
    return img_path