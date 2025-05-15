# app.py
from flask import Flask, render_template, send_from_directory, url_for
from pathlib import Path

app = Flask(__name__)
app.config["ROOT_DIR"] = Path(app.root_path)
app.config["GAMES_DIR"] = app.config["ROOT_DIR"] / "games"
app.config["ASSETS_DIR"] = app.config["ROOT_DIR"] / "assets"
app.config["DEFAULT_ICON"] = "default-game-icon.png"
app.config["SITE_TITLE"] = "Игровой портал от Sarcandi"
app.config["GITHUB_URL"] = "https://github.com/Sarcandi"
app.config["TELEGRAM_URL"] = "https://t.me/sarcandi"


def get_game_title(game_dir):
    index_file = game_dir / "index.html"
    if index_file.exists():
        try:
            with open(index_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "<title>" in content:
                    start = content.find("<title>") + 7
                    end = content.find("</title>", start)
                    return content[start:end].strip()
        except:
            pass
    return game_dir.name


def get_games_list():
    games_dir = app.config["GAMES_DIR"]
    if not games_dir.is_dir():
        raise FileNotFoundError("Директория с играми не найдена")

    games = []
    for item in games_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            game_title = get_game_title(item)
            games.append(
                {
                    "dir_name": item.name,
                    "title": game_title,
                    "author": item.name,  # Используем имя папки как автора
                }
            )

    return sorted(games, key=lambda x: x["title"].casefold()) if games else []


@app.route("/")
def index():
    try:
        games = get_games_list()
        if not games:
            raise ValueError("На данный момент игр нет в каталоге")

        return render_template("index.html", games=games, config=app.config)
    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/games/<game>/<path:filename>")
def serve_game(game, filename):
    return send_from_directory(app.config["GAMES_DIR"] / game, filename)


@app.route("/assets/<path:filename>")
def serve_asset(filename):
    return send_from_directory(app.config["ASSETS_DIR"], filename)


@app.context_processor
def inject_utilities():
    def get_game_icon(game):
        icon_path = app.config["GAMES_DIR"] / game / "icon.png"
        if icon_path.exists():
            return url_for("serve_game", game=game, filename="icon.png")
        return url_for("serve_asset", filename=app.config["DEFAULT_ICON"])

    return dict(
        get_game_icon=get_game_icon,
        site_title=app.config["SITE_TITLE"],
        github_url=app.config["GITHUB_URL"],
        telegram_url=app.config["TELEGRAM_URL"],
    )


if __name__ == "__main__":
    app.run()
