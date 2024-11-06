import re
import os
import yaml
import markdown
import shutil
from jinja2 import Environment, FileSystemLoader
from markdown.extensions import fenced_code, tables
from markdown.extensions.footnotes import FootnoteExtension
from markdown_katex import KatexExtension
from custom_markdown_extension import FigureExtension

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

def process_title(title):
    return title.split(':')[0].strip()

def read_markdown_files():
    posts = []
    for filepath in os.listdir('content/posts'):
        if filepath.endswith('.md'):
            with open(os.path.join('content/posts', filepath), 'r', encoding='utf-8') as file:
                content = file.read()
                _, frontmatter, body = content.split('---', 2)
                metadata = yaml.safe_load(frontmatter)
                
                # Extract title from the first # in the body
                title_match = re.search(r'^#\s*(.+)$', body, re.MULTILINE)
                title = title_match.group(1) if title_match else os.path.splitext(filepath)[0]
                
                posts.append({
                    "title": title,
                    "short_title": process_title(title),
                    "date": metadata["date"],
                    "tags": metadata.get("tags", []),
                    "read_time": metadata.get("readTime", "N/A"),
                    "filename": os.path.splitext(filepath)[0]
                })
    return sorted(posts, key=lambda x: x["date"], reverse=True)

def generate_index():
    template = env.get_template('index.html')
    posts = read_markdown_files()[:3]  # Get the 3 most recent posts
    html = template.render(recent_posts=posts)
    with open('output/index.html', 'w', encoding='utf-8') as file:
        file.write(html)

def generate_posts():
    template = env.get_template('post.html')
    
    for filepath in os.listdir('content/posts'):
        if filepath.endswith('.md'):
            # Create a new Markdown instance for each post
            md = markdown.Markdown(extensions=[
                'fenced_code', 
                'tables', 
                FootnoteExtension(UNIQUE_IDS=True),
                KatexExtension(),
                FigureExtension()
            ])
            
            with open(os.path.join('content/posts', filepath), 'r', encoding='utf-8') as file:
                content = file.read()
                _, frontmatter, body = content.split('---', 2)
                metadata = yaml.safe_load(frontmatter)
                
                # Extract title from the first # in the body
                title_match = re.search(r'^#\s*(.+)$', body, re.MULTILINE)
                title = title_match.group(1) if title_match else metadata.get('title', os.path.splitext(filepath)[0])
                
                # Remove the title from the body
                body = re.sub(r'^#\s*.+\n', '', body, 1, re.MULTILINE)
                
                post_filename = os.path.splitext(filepath)[0]
                
                # Copy images and update their paths
                body = copy_post_images(body, post_filename)
                
                html_content = md.convert(body)
                html = template.render(
                    title=title,
                    content=html_content,
                    metadata=metadata,
                    img_path=f"/static/images/posts/{post_filename}.png"
                )
                with open(f'output/{post_filename}.html', 'w', encoding='utf-8') as output_file:
                    output_file.write(html)

def copy_post_images(content, post_filename):
    img_pattern = r'!\[.*?\]\((.*?)\)'
    matches = re.findall(img_pattern, content)
    
    for img_path in matches:
        src_path = os.path.join('content', img_path.lstrip('/'))
        dst_dir = os.path.join('output', 'static', 'images', 'posts', post_filename)
        os.makedirs(dst_dir, exist_ok=True)
        dst_path = os.path.join(dst_dir, os.path.basename(img_path))
        shutil.copy(src_path, dst_path)
    
    return content.replace('](/images/', f'](/static/images/posts/{post_filename}/')

def generate_blog_listings():
    template = env.get_template('archive.html')
    posts = read_markdown_files()
    html = template.render(posts=posts)
    with open('output/archive.html', 'w', encoding='utf-8') as file:
        file.write(html)

def generate_skilltree():
    template = env.get_template('skilltree.html')
    html = template.render()
    with open('output/skilltree.html', 'w', encoding='utf-8') as file:
        file.write(html)

def main():
    os.makedirs('output', exist_ok=True)
    generate_index()
    generate_blog_listings()
    generate_posts()
    # generate_skilltree()
    
    # Copy static files to output directory
    copy_static_files()
    
    # Copy CNAME file to output directory
    shutil.copy('CNAME', 'output/CNAME')
    
    # Add .nojekyll file
    with open('output/.nojekyll', 'w') as f:
        pass
    
    print("Static site generated successfully.")

def copy_static_files():
    shutil.copytree('static', 'output/static', dirs_exist_ok=True)

if __name__ == "__main__":
    main()
