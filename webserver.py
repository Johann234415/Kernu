from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    ascii_art = """
    <pre style="font-family: monospace; color: #00ff00; background-color: #000; padding: 20px; text-align: center;">
██   ██ ███████ ██████     ███    ██ ██    ██ 
██  ██  ██      ██   ██    ████   ██ ██    ██ 
█████   █████   ██████     ██ ██  ██ ██    ██ 
██  ██  ██      ██   ██    ██  ██ ██ ██    ██ 
██   ██ ███████ ██   ██ ██ ██   ████  ██████  
    </pre>
    <div style="color: #ff0000; text-align: center; font-family: Arial;">
        <h2>KER.NU Discord Nuker Bot - ONLINE</h2>
        <p>Bot Status: <span style="color: #00ff00;">ACTIVE</span></p>
    </div>
    """
    return ascii_art

def run():
    app.run(host="0.0.0.0", port=8080) #don't touch this

def keep_alive():
    server = Thread(target=run)
    server.start()