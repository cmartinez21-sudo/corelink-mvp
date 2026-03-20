import sys
import os
from pathlib import Path
from flask import Flask, render_template

sys.path.insert(0, str(Path(__file__).parent))
from database import get_stats, init_db
from reply_checker import check_replies

app = Flask(__name__, template_folder=str(Path(__file__).parent.parent / "templates"))


@app.route("/")
def index():
    check_replies()
    stats = get_stats()
    return render_template("dashboard.html", stats=stats)


if __name__ == "__main__":
    init_db()
    import webbrowser
    webbrowser.open("http://localhost:5050")
    app.run(port=5050, debug=False)
