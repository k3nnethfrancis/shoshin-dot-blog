import re
import os
import yaml
import markdown
import shutil
from jinja2 import Environment, FileSystemLoader
from markdown.extensions import fenced_code, tables
from markdown.extensions.footnotes import FootnoteExtension
from markdown_katex import KatexExtension

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

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
                KatexExtension()
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
                
                html_content = md.convert(body)
                post_filename = os.path.splitext(filepath)[0]
                html = template.render(
                    title=title,
                    content=html_content,
                    metadata=metadata,
                    img_path=f"/static/images/posts/{post_filename}.png"
                )
                os.makedirs('output/post', exist_ok=True)
                with open(f'output/post/{post_filename}.html', 'w', encoding='utf-8') as output_file:
                    output_file.write(html)

# We can remove the process_latex function as it's no longer needed
# def process_latex(content):
#     ...
    
def generate_listings():
    template = env.get_template('listings.html')
    posts = read_markdown_files()
    html = template.render(posts=posts)
    with open('output/listings.html', 'w', encoding='utf-8') as file:
        file.write(html)

def generate_skilltree():
    template = env.get_template('skilltree.html')
    html = template.render()
    with open('output/skilltree.html', 'w', encoding='utf-8') as file:
        file.write(html)

def main():
    os.makedirs('output', exist_ok=True)
    generate_index()
    generate_listings()
    generate_posts()
    generate_skilltree()
    
    # Copy static files to output directory
    shutil.copytree('static', 'output/static', dirs_exist_ok=True)
    
    # Copy CNAME file to output directory
    shutil.copy('CNAME', 'output/CNAME')
    
    # Add .nojekyll file
    with open('output/.nojekyll', 'w') as f:
        pass
    
    print("Static site generated successfully.")

if __name__ == "__main__":
    main()