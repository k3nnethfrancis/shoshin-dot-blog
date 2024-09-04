"""
FastAPI application for a personal blog.

This module sets up a FastAPI application to serve a personal blog with
markdown-based posts, caching, and image generation capabilities.
"""

import os
import logging
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Any

import glob
import yaml
import markdown2
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from image_generator import generate_post_image
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI."""
    # Initialize the FastAPI cache
    FastAPICache.init(InMemoryBackend())
    yield
    # Cleanup code (if any) goes here

app = FastAPI(lifespan=lifespan)

# CORS middleware setup
ALLOWED_ORIGINS = [
    "https://k3nn.computer",
    "https://k3nn-dot-computer-b1daf058c82e.herokuapp.com",  # Heroku app URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static file directories
STATIC_DIRS = {
    "/static": "static",
    "/pages": "pages",
    "/components": "components",
    "/assets": "assets",
}

for route, directory in STATIC_DIRS.items():
    app.mount(route, StaticFiles(directory=directory), name=directory)

# Set up Jinja2 templates
templates = Jinja2Templates(directory="pages")


def read_markdown_files() -> List[Dict[str, Any]]:
    """
    Read and parse all markdown files in the 'posts' directory.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing post information,
                              sorted by date (newest first).
    """
    posts = []
    for filepath in glob.glob("posts/*.md"):
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            _, frontmatter, body = content.split('---', 2)
            metadata = yaml.safe_load(frontmatter)

            # Extract title from the first line of the body
            title = body.strip().split('\n')[0].lstrip('# ').strip()

            # Handle the date whether it's a string or already a date object
            post_date = metadata["date"]
            if isinstance(post_date, str):
                post_date = datetime.strptime(post_date, "%Y-%m-%d").date()
            elif not isinstance(post_date, date):
                raise ValueError(f"Unexpected date format in {filepath}")

            posts.append({
                "title": title,
                "date": post_date,
                "tags": metadata.get("tags", []),
                "read_time": metadata.get("readTime", "N/A"),
                "filename": Path(filepath).stem
            })

    # Sort posts by date, newest first
    return sorted(posts, key=lambda x: x["date"], reverse=True)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render the home page with the 3 most recent blog posts."""
    posts = read_markdown_files()[:3]  # Get the 3 most recent posts
    return templates.TemplateResponse("index.html", {"request": request, "recent_posts": posts})


@app.get("/listings", response_class=HTMLResponse)
async def read_listings(request: Request):
    """Render the blog listings page with all posts."""
    posts = read_markdown_files()
    return templates.TemplateResponse("listings.html", {"request": request, "posts": posts})


@app.get("/post/{post_name}", response_class=HTMLResponse)
async def read_post(request: Request, post_name: str):
    """
    Render a specific blog post.

    Args:
        request (Request): The FastAPI request object.
        post_name (str): The name of the post to render.

    Raises:
        HTTPException: If the post is not found.
    """
    logger.info("Accessing post: %s", post_name)
    filepath = Path(f"posts/{post_name}.md")
    if not filepath.exists():
        logger.error("Post not found: %s", filepath)
        raise HTTPException(status_code=404, detail="Post not found")

    content = filepath.read_text(encoding="utf-8")
    md = markdown2.Markdown(extras=["metadata"])
    html = md.convert(content)
    metadata = md.metadata

    # Generate image if it doesn't exist
    img_path = Path(f"assets/img/{post_name}.png")
    if not img_path.exists():
        img_path = generate_post_image(content, metadata.get("title", post_name))

    # Ensure img_path is relative to the static directory
    img_path = str(img_path).replace("assets/", "")

    logger.info("Successfully rendered post: %s", post_name)
    return templates.TemplateResponse(
        "post.html",
        {
            "request": request,
            "content": html,
            "metadata": metadata,
            "img_path": img_path
        }
    )


@app.get("/skilltree", response_class=HTMLResponse)
async def read_skill_tree(request: Request):
    """Render the skill tree page."""
    return templates.TemplateResponse("skilltree.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)