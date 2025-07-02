from flask import Flask
from routes import main
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.register_blueprint(main)

if __name__ == "__main__":
    app.run(debug=True)