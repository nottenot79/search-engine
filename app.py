from flask import Flask
from routes import register_routes
import subprocess
import os

# Initialize Flask App
app = Flask(__name__)

# Register all routes
register_routes(app)

# Choose the tunnel service (ngrok, localtunnel, cloudflare, serveo)
TUNNEL_SERVICE = "localtunnel"  # Change this to "ngrok", "cloudflare", or "serveo"

def start_tunnel():
    if TUNNEL_SERVICE == "ngrok":
        from pyngrok import ngrok
        public_url = ngrok.connect(5000).public_url
        print(f"Ngrok URL: {public_url}")

    elif TUNNEL_SERVICE == "localtunnel":
        print("Starting LocalTunnel...")
        subprocess.Popen(["lt", "--port", "5000"])
        print("LocalTunnel started.")

    elif TUNNEL_SERVICE == "cloudflare":
        print("Starting Cloudflare Tunnel...")
        subprocess.Popen(["cloudflared", "tunnel", "--url", "http://localhost:5000"])
        print("Cloudflare Tunnel started.")

    elif TUNNEL_SERVICE == "serveo":
        print("Starting Serveo Tunnel...")
        subprocess.Popen(["ssh", "-R", "80:localhost:5000", "serveo.net"])
        print("Serveo Tunnel started.")

    else:
        print("No tunnel service selected.")

if __name__ == "__main__":
    #start_tunnel()  # Start the selected tunnel
    app.run(host="0.0.0.0", port=5000, debug=True)
