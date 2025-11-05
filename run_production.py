from website import create_app
from waitress import serve
import os

app = create_app()

port = int(os.environ.get("PORT", 8000))  # Render te da PORT
serve(app, host="0.0.0.0", port=port, threads=4)
