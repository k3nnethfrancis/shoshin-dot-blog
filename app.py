import os
import logging
import glob
import markdown2
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from dotenv import load_dotenv
from datetime import datetime, date
from image_generator import generate_post_image
import yaml

# Load environment variables at the very beginning of your app
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)

app = FastAPI()

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/posts", StaticFiles(directory="posts"), name="posts")

# Set up Jinja2 templates, now using the "pages" directory
pages = Jinja2Templates(directory="pages")

# Ollama API URL
OLLAMA_API_URL = "http://localhost:1337"

class ChatRequest(BaseModel):
    message: str

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def read_markdown_files():
    posts = []
    for filepath in glob.glob("posts/*.md"):
        with open(filepath, "r") as file:
            content = file.read()
            _, frontmatter, body = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)
            
            title = body.strip().split('\n')[0].lstrip('# ').strip()
            
            # Handle the date whether it's a string or already a date object
            post_date = metadata["date"]
            if isinstance(post_date, str):
                post_date = datetime.strptime(post_date, "%Y-%m-%d").date()
            elif isinstance(post_date, date):
                post_date = post_date
            else:
                raise ValueError(f"Unexpected date format in {filepath}")

            posts.append({
                "title": title,
                "date": post_date,
                "tags": metadata.get("tags", []),
                "read_time": metadata.get("readTime", "N/A"),
                "filename": os.path.basename(filepath).replace(".md", "")
            })
    
    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return pages.TemplateResponse("index.html", {"request": request})

@app.get("/listings", response_class=HTMLResponse)
async def read_listings(request: Request):
    posts = read_markdown_files()
    return pages.TemplateResponse("listings.html", {"request": request, "posts": posts})

@app.get("/post/{post_name}", response_class=HTMLResponse)
async def read_post(request: Request, post_name: str):
    logging.info(f"Accessing post: {post_name}")
    filepath = f"posts/{post_name}.md"
    if not os.path.exists(filepath):
        logging.error(f"Post not found: {filepath}")
        raise HTTPException(status_code=404, detail="Post not found")
    
    with open(filepath, "r") as file:
        content = file.read()
        md = markdown2.Markdown(extras=["metadata"])
        html = md.convert(content)
        metadata = md.metadata
        
        # Generate image if it doesn't exist
        img_path = f"assets/img/{post_name}.png"
        if not os.path.exists(img_path):
            img_path = generate_post_image(content, metadata.get("title", post_name))
        
        # Ensure img_path is relative to the static directory
        img_path = img_path.replace("assets/", "")
        
        logging.info(f"Successfully rendered post: {post_name}")
        return pages.TemplateResponse(
            "post.html", 
            {
                "request": request, 
                "content": html, 
                "metadata": metadata,
                "img_path": img_path
            }
        )

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        logging.info(f"Received message: {request.message}")
        
        # Prepare the request for the Ollama API
        ollama_request = {
            "message": request.message
        }
        
        # Send the request to the Ollama API
        response = requests.post(f"{OLLAMA_API_URL}/chat", json=ollama_request)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        ollama_response = response.json()
        logging.info(f"Response from model: {ollama_response['response']}")
        
        return {"response": ollama_response['response']}
    except requests.RequestException as e:
        logging.error(f"Error communicating with Ollama API: {str(e)}")
        raise HTTPException(status_code=500, detail="Error communicating with AI model")
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)