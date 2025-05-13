# Shoshin Blog - Project Overview

## Introduction

This document provides a comprehensive overview of the Shoshin Blog project, a static site generator for a personal blog hosted at [shoshin.blog](https://shoshin.blog). The project utilizes Python, Markdown, and Jinja2 to convert content into a fully static website.

## Project Structure

The project follows this directory structure:

```
/shoshin-dot-blog/
├── content/            # Raw content for the blog
│   ├── drafts/         # Work-in-progress posts
│   ├── images/         # Referenced images in posts
│   └── posts/          # Markdown post files
├── static/             # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── images/         # Generated post images and other assets
├── templates/          # Jinja2 HTML templates
│   ├── base.html       # Base template with common elements
│   ├── index.html      # Homepage template
│   ├── post.html       # Individual post template
│   ├── archive.html    # Archive/blog listing template
│   └── skilltree.html  # Skill tree page template
├── output/             # Generated static site (not in git)
├── site_generator.py   # Main site generation script
├── image_generator.py  # AI-powered image generation for posts
├── custom_markdown_extension.py # Custom MD extension for figures
├── serve.py            # Local development server
└── requirements.txt    # Python dependencies
```

## Core Workflow

The blog generation process follows these steps:

1. **Content Creation**:
   - Write posts in Markdown with YAML frontmatter
   - Place in `content/posts/` directory
   - Frontmatter contains metadata like date, tags, and read time

2. **Image Generation**:
   - Run `image_generator.py` to create AI-generated banner images
   - Uses OpenAI/Anthropic to create image prompts and DALL-E for generation
   - Images are automatically cropped and stored in `static/images/posts/`
   - Post frontmatter is updated with image path reference

3. **Site Generation**:
   - Run `site_generator.py` to process all content
   - Converts Markdown to HTML with custom extensions
   - Applies templates using Jinja2
   - Copies static assets to output directory
   - Creates index, post, and archive pages

4. **Development & Viewing**:
   - Use `serve.py` for local development with auto-reload
   - Files are served from the `output/` directory
   - Changes to content, templates, or static files trigger regeneration

5. **Deployment**:
   - The `output/` directory contains the complete static site
   - GitHub Pages deployment configuration via CNAME file
   - `.nojekyll` ensures GitHub doesn't process the files with Jekyll

## Technology Stack

- **Python**: Core language for generation scripts
- **Markdown**: Content format with custom extensions
- **Jinja2**: Templating engine for HTML generation
- **OpenAI/Anthropic**: AI APIs for image prompt generation
- **DALL-E**: AI image generation for post banners
- **LiveReload**: Local development server with auto-refresh

## Key Features

- **Custom Markdown Processing**: Extensions for figures, KaTeX, and code highlighting
- **AI-Powered Image Generation**: Automatic banner images for posts
- **Responsive Design**: Mobile-friendly layouts
- **Dark Mode Support**: Color scheme following system preferences
- **Typing Effect**: Custom JavaScript animations on homepage

## Future Development

Potential areas for enhancement:

- SEO optimization
- RSS feed generation
- Tag-based navigation
- Reading time calculation
- Comment system integration

---

*This documentation was created on 2025-05-12 and may need updates as the project evolves.*