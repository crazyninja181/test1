from flask import Flask, request, jsonify, render_template_string, send_from_directory
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

latest_message = ""       # stores latest text message
latest_voice = None       # stores latest uploaded voice filename

# -------------- Home Page (for Web User) ----------------
page = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Assistive Device Message Center</title>
  <style>
    body {font-family:Arial;background:#f3f4f6;display:flex;
          flex-direction:column;align-items:center;justify-content:center;height:100vh;}
    .card {background:white;padding:30px;border-radius:15px;
           box-shadow:0 0 15px rgba(0,0,0,0.1);width:340px;text-align:center;}
    input,button{padding:10px;margin:8px;width:90%;border-radius:6px;border:1px solid #ccc;}
    button{background:#2563eb;color:white;border:none;cursor:pointer;}
    button:hover{background:#1d4ed8;}
  </style>
</head>
<body>
  <div class="card">
    <h2>📨 Send Text Message to Raspberry Pi</h2>
    <form method="POST" action="/send">
      <input type="text" name="message" placeholder="Enter your message here" required />
      <button type="submit">Send</button>
    </form>
    <hr>
    <a href="/voice">🎧 Listen to Latest Voice Message</a>
  </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(page)

# ----------- Send message from web to Pi -----------
@app.route("/send", methods=["POST"])
def send_message():
    global latest_message
    latest_message = request.form.get("message", "")
    print(f"📩 New text message: {latest_message}")
    return f"<h3>✅ Message Sent!</h3><p>{latest_message}</p><a href='/'>Back</a>"

# ----------- Raspberry Pi fetches text -----------
@app.route("/get", methods=["GET"])
def get_message():
    """Raspberry Pi polls this to get the latest text message."""
    return jsonify({"message": latest_message})

# ----------- Pi uploads voice message -----------
@app.route("/upload", methods=["POST"])
def upload_voice():
    global latest_voice
    if 'file' not in request.files:
        return "No file uploaded", 400
    f = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, f.filename)
    f.save(filepath)
    latest_voice = f.filename
    print(f"🎙️ New voice message received: {f.filename}")
    return "File uploaded successfully"

# ----------- Web plays latest voice -----------
@app.route("/voice")
def play_voice():
    if not latest_voice:
        return "<h3>No voice message yet.</h3><a href='/'>Back</a>"
    return f"""
    <h3>🎧 Latest Voice Message:</h3>
    <audio controls>
      <source src="/uploads/{latest_voice}" type="audio/wav">
      Your browser does not support audio.
    </audio>
    <br><a href="/">Back</a>
    """

@app.route("/uploads/<path:filename>")
def serve_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ----------- Start app (Render-compatible port) -----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # for Render compatibility
    app.run(host="0.0.0.0", port=port, debug=True)
