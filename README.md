# shoshin-dot-blog

this is the repo behind my personal blog. see it live at [shoshin.blog](https://shoshin.blog).

---

## How to add a new post

1. **Write your post in Markdown**
   - Place your file in `content/posts/{post-name}.md`.
   - Use YAML frontmatter at the top, e.g.:
     ```yaml
     ---
     date: 2024-06-01
     tags: [tag1, tag2]
     readTime: 5 minutes
     ---
     # My Post Title

     Your post content here...
     ```
   - The filename (without `.md`) will be used as the post's slug and for image generation.

2. **Generate a post image**
   - Run the image generator script:
     - For all posts: `python image_generator.py --all`
     - For a specific post: `python image_generator.py --posts {post-name}`
   - This will create an image at `static/images/posts/{post-name}.png` and update the markdown frontmatter with the image path.

3. **Generate the static site**
   - Run: `python site_generator.py`
   - This will:
     - Convert all markdown posts to HTML in `output/`
     - Update the homepage with the 3 most recent posts
     - Update the archive with all posts
     - Copy static assets (CSS, JS, images) to `output/`

4. **View locally or deploy**
   - Serve the `output/` directory with a static file server (e.g., `python -m http.server`)
   - Or push the contents of `output/` to your GitHub Pages branch

---

**Relevant directories:**
- `content/posts/`: Your markdown posts
- `static/images/posts/`: Post images
- `static/css/`, `static/js/`: Styling and scripts
- `templates/`: HTML templates
- `output/`: The generated static site
- `image_generator.py`: Generates images for posts
- `generate_static_site.py`: Builds the static site