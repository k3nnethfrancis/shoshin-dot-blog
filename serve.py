'''
This module is for local development.
'''

from livereload import Server, shell
import site_generator

def generate():
    site_generator.main()

# Run the site generator
generate()

# Create a server
server = Server()

# Watch for changes in content, templates, and static files
server.watch('content/', generate)
server.watch('templates/', generate)
server.watch('static/', generate)

# Serve the output directory
server.serve(root='output')