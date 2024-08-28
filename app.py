import os
from pathlib import Path
import logging
import glob
import yaml
import markdown2
from datetime import datetime, date

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from pydantic import BaseModel
import httpx

from dotenv import load_dotenv
from image_generator import generate_post_image

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3333",
        "http://0.0.0.0:3333",
        "http://127.0.0.1:3333",
        "http://localhost:1337",
        "http://0.0.0.0:1337",
        "http://127.0.0.1:1337",
        "https://k3nn.computer",
        "https://k3nn-dot-computer-b1daf058c82e.herokuapp.com",  # Heroku app URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTPS redirect middleware
app.add_middleware(HTTPSRedirectMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/pages", StaticFiles(directory="pages"), name="pages")
app.mount("/components", StaticFiles(directory="components"), name="components")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Set up Jinja2 templates
pages = Jinja2Templates(directory="pages")

# Hugging Face API configuration
HUGGING_FACE_API_TOKEN = os.getenv("HUGGING_FACE_API_TOKEN")
HF_API_URL = "https://api-inference.huggingface.co/models/cognitivecomputations/dolphin-2.9.4-llama3.1-8b"

class ChatRequest(BaseModel):
    inputs: str
    parameters: dict

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
    posts = read_markdown_files()[:3]  # Get the 3 most recent posts
    return pages.TemplateResponse("index.html", {"request": request, "recent_posts": posts})

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

@app.get("/timeline", response_class=HTMLResponse)
async def read_my_work(request: Request):
    return pages.TemplateResponse("timeline.html", {"request": request})

@app.get("/terminal", response_class=HTMLResponse)
async def terminal_page(request: Request):
    return pages.TemplateResponse("terminal.html", {"request": request})

@app.post("/api/chat")
async def chat(request: ChatRequest):
    logging.info(f"Received chat request: {request}")
    try:
        headers = {
            "Authorization": f"Bearer {HUGGING_FACE_API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(HF_API_URL, json=request.dict(), headers=headers)
        
        if response.status_code != 200:
            logging.error(f"Hugging Face API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=f"Error from Hugging Face API: {response.text}")
        
        result = response.json()
        ai_response = result[0]['generated_text'].split('<|im_start|>assistant\n')[1].split('<|im_end|>')[0].strip()
        
        return {"generated_text": ai_response}
    except Exception as e:
        logging.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)