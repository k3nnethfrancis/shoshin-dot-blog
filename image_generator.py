import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from PIL import Image
import requests
from io import BytesIO
import re
import yaml
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

openai_client = OpenAI(api_key=openai_api_key)
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_image_prompt(post_content, client='openai'):
    """Generate an image prompt using Claude or GPT."""
    logging.info(f"Generating image prompt using {client}")
    system_prompt = (
        "You are an AI assistant tasked with creating image prompts for blog posts. "
        "Given the content of a blog post, create a concise and vivid prompt for "
        "an image that captures the essence of the post. The prompt should be "
        "suitable for an AI image generation model like DALL-E. "
        "Styles we like are glitch, pixel art, and retro, bladerunner, and cyberpunk, trippy, and renaissance surreal."
    )
    if client == 'anthropic':
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=100,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Create an image prompt for this blog post:\n\n{post_content}"}
            ]
        )
        return response.content[0].text.strip()
    elif client == 'openai':
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": post_content}
            ]
        )
        return response.choices[0].message.content
    else:
        raise ValueError(f"Invalid client: {client}")

def generate_and_save_image(prompt, filename):
    """Generate an image using DALL-E, crop it, and save it."""
    logging.info(f"Generating image for: {filename}")
    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    
    logging.info(f"Image generated, downloading from: {image_url}")
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
    os.makedirs("static/images/posts", exist_ok=True)
    
    # Save the cropped image
    img_path = f"static/images/posts/{filename}.png"
    
    logging.info(f"Image saved: {img_path}")
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

def process_all_posts():
    """Process all markdown files in the posts directory."""
    posts_dir = 'posts'
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            logging.info(f"Processing file: {filename}")
            file_path = os.path.join(posts_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                _, frontmatter, body = content.split('---', 2)
                metadata = yaml.safe_load(frontmatter)
                title = metadata.get('title', os.path.splitext(filename)[0])
                
                logging.info(f"Generating image for post: {title}")
                generate_post_image(body, title)

if __name__ == "__main__":
    logging.info("Starting image generation process")
    process_all_posts()
    logging.info("Image generation process completed")