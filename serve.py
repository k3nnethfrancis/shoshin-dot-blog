'''
This module is for local development.
'''

from livereload import Server, shell
import site_generator
import socket

def generate():
    print("Generating site...")
    site_generator.main()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Run the site generator
generate()

# Create a server
print("Creating server...")
server = Server()

# Watch for changes in content, templates, and static files
server.watch('content/', generate)
server.watch('templates/', generate)
server.watch('static/', generate)

# Get the local IP address
local_ip = get_local_ip()

print(f"Server running on:")
print(f"Local:   http://localhost:5500")
print(f"Network: http://{local_ip}:5500")
print("Use the Network address to access from other devices on your Wi-Fi.")

# Serve the output directory
server.serve(root='output', host='0.0.0.0', port=5500)