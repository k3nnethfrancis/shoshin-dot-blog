import os
import argparse
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic
from PIL import Image
import requests
from io import BytesIO
import re
import yaml
import logging
import base64
from datetime import datetime

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
        "Given the content of a blog post, create prompt to generate an image "
        "that captures the essence of the post. The prompt should be "
        "suitable for an AI image generation model like DALL-E. "
        "You should focus on an abstract concept that is related to the post. "
        "Approved style is monochramatic moebius glitch manga solarpunk."
        "Do not use any words or people or references to them in the prompt."
        # "Artists like Moebius, Yoshitaka Amano, Kazuo Koike, Akira Toriyama, and others can be used as inspiration. "
        # "You should try to pick specific styles rather than blending them all together."
    )
    if client == 'anthropic':
        response = anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=400,
            temperature=1.0,
            system=system_prompt,
            messages=[
                {"role": "user", "content": f"Create an image prompt for this blog post:\n\n{post_content}"}
            ]
        )
        return response.content[0].text.strip()
    elif client == 'openai':
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"# Blog Post\n\n{post_content}"}
            ]
        )
        return response.choices[0].message.content
    else:
        raise ValueError(f"Invalid client: {client}")

def generate_and_save_image(prompt, filename, post_content, max_retries=3):
    """Generate image, save raw with timestamp, crop, save final, and return path."""
    for attempt in range(max_retries):
        try:
            logging.info(f"Generating image for: {filename} (attempt {attempt+1})")
            response = openai_client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                n=1,
                size="1536x1024",
                quality="high"
            )
            image_base64 = getattr(response.data[0], "b64_json", None)
            if not image_base64:
                logging.error(f"No image data returned from OpenAI. Full response: {response}")
                raise ValueError("No image data returned from OpenAI.")
            image_bytes = base64.b64decode(image_base64)
            img = Image.open(BytesIO(image_bytes))

            # --- Save the raw, uncropped image with timestamp ---
            os.makedirs("raw_images", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            raw_img_filename = f"{filename}_{timestamp}.png"
            raw_img_path = os.path.join("raw_images", raw_img_filename)
            img.save(raw_img_path, format="PNG")
            logging.info(f"Raw image saved: {raw_img_path}")
            # ----------------------------------------------------

            # --- Crop and save the final banner image --- 
            width, height = img.size
            new_height = height // 3
            top = (height - new_height) // 2
            bottom = top + new_height
            cropped_img = img.crop((0, top, width, bottom))
            os.makedirs("static/images/posts", exist_ok=True)
            final_img_filename = f"{filename}.jpg"
            final_img_path = os.path.join("static/images/posts", final_img_filename)
            cropped_img.save(final_img_path, format="JPEG", quality=85, optimize=True)
            logging.info(f"Cropped image saved: {final_img_path}")
            # -------------------------------------------

            return final_img_path
        except Exception as e:
            if hasattr(e, 'code') and getattr(e, 'code', None) == 'moderation_blocked':
                logging.warning(f"Moderation blocked prompt for {filename}. Retrying with a new prompt.")
                prompt = generate_image_prompt(post_content)  # Regenerate prompt
                continue
            logging.error(f"Error generating image for {filename}: {e}")
            break
    logging.error(f"Failed to generate image for {filename} after {max_retries} attempts. Skipping.")
    return None

def sanitize_filename(filename):
    """Sanitize the filename to be safe for file systems."""
    return re.sub(r'[^\w\-_\. ]', '_', filename)

def generate_post_image(post_content, post_title):
    """Main function to generate and save an image for a blog post."""
    prompt = generate_image_prompt(post_content)
    sanitized_title = sanitize_filename(post_title)
    img_path = generate_and_save_image(prompt, sanitized_title, post_content)
    return img_path

def process_post(file_path, force=False):
    """Process a single post file."""
    logging.info(f"Processing file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        _, frontmatter, body = content.split('---', 2)
        metadata = yaml.safe_load(frontmatter)
        title = metadata.get('title', os.path.splitext(os.path.basename(file_path))[0])
        
        existing_image = metadata.get('image')
        if existing_image and not force:
            logging.info(f"Image already exists for {title}. Skipping.")
            return
        
        logging.info(f"Generating image for post: {title}")
        img_path = generate_post_image(body, title)
        
        if img_path:  # Only update if image generation was successful
            # Update the frontmatter with the generated image path
            metadata['image'] = '/' + img_path
            updated_frontmatter = yaml.dump(metadata, default_flow_style=False)
            
            # Write the updated content back to the file
            updated_content = f"---\n{updated_frontmatter}---\n{body}"
            with open(file_path, 'w', encoding='utf-8') as updated_file:
                updated_file.write(updated_content)
            
            logging.info(f"Updated frontmatter for {title} with new image path: {img_path}")
        else:
            logging.warning(f"Skipping frontmatter update for {title} as image generation failed.")

def process_all_posts(force=False):
    """Process all markdown files in the posts directory."""
    posts_dir = 'content/posts'
    for filename in os.listdir(posts_dir):
        if filename.endswith('.md'):
            file_path = os.path.join(posts_dir, filename)
            process_post(file_path, force)

def main():
    parser = argparse.ArgumentParser(description="Generate images for blog posts.")
    parser.add_argument("--all", action="store_true", help="Generate images for all posts")
    parser.add_argument("--force", action="store_true", help="Force regeneration of images even if they already exist")
    parser.add_argument("--posts", nargs="+", help="Generate images for specific posts (provide filenames or base names)")
    parser.add_argument("--missing", action="store_true", help="Generate images only for posts without existing images")

    args = parser.parse_args()

    posts_dir = 'content/posts'

    if args.all:
        logging.info("Generating images for all posts")
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(posts_dir, filename)
                process_post(file_path, force=args.force)
    elif args.posts:
        logging.info(f"Generating images for specified posts: {args.posts}")
        for post in args.posts:
            if not post.endswith('.md'):
                post += '.md'
            file_path = os.path.join(posts_dir, post)
            if os.path.exists(file_path):
                process_post(file_path, force=args.force)
            else:
                logging.warning(f"Post file not found: {post}")
    elif args.missing:
        logging.info("Checking for posts without existing images")
        missing_images_count = 0
        for filename in os.listdir(posts_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(posts_dir, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    _, frontmatter, _ = content.split('---', 2)
                    metadata = yaml.safe_load(frontmatter)
                    if 'image' not in metadata:
                        process_post(file_path, force=False)
                        missing_images_count += 1
        
        if missing_images_count == 0:
            logging.info("No missing images found. All posts have images.")
        else:
            logging.info(f"Generated images for {missing_images_count} posts.")
    else:
        logging.error("No action specified. Use --all, --posts, or --missing")

if __name__ == "__main__":
    main()
