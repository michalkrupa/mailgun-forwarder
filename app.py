from flask import Flask

from mailgun.request import LargeRequest
from mailgun.forwarder.routes import bp

app = Flask(__name__)
app.request_class = LargeRequest
app.config['MAX_CONTENT_LENGTH'] = 300 * 1024 * 1024
app.config['ENV'] = "production"
app.config['DEBUG'] = False
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8765, debug=True)

