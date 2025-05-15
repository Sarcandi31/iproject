from flask import Flask, render_template, send_from_directory, url_for
from pathlib import Path
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

app = Flask(__name__)
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1
)  # Для корректной работы за прокси

# Конфигурация
BASE_DIR = Path(__file__).parent
app.config.update(
    GAMES_DIR=BASE_DIR / "games",
    ASSETS_DIR=BASE_DIR / "assets",
    DEFAULT_ICON="default-game-icon.png",
    SITE_TITLE="Игровой портал от Sarcandi",
    GITHUB_URL="https://github.com/Sarcandi",
    TELEGRAM_URL="https://t.me/sarcandi",
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,  # Ограничение загрузки 16MB
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_game_title(game_dir: Path) -> str:
    """Извлекает заголовок игры из index.html или использует имя папки"""
    index_file = game_dir / "index.html"
    if not index_file.exists():
        return game_dir.name

    try:
        with open(index_file, "r", encoding="utf-8") as f:
            content = f.read()
            if "<title>" in content:
                start = content.find("<title>") + 7
                end = content.find("</title>", start)
                return content[start:end].strip() or game_dir.name
    except Exception as e:
        logger.error(f"Ошибка чтения {index_file}: {e}")

    return game_dir.name


def get_games_list() -> list:
    """Возвращает отсортированный список игр"""
    games_dir = app.config["GAMES_DIR"]
    if not games_dir.is_dir():
        raise FileNotFoundError("Директория с играми не найдена")

    games = []
    for item in games_dir.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            games.append(
                {
                    "dir_name": item.name,
                    "title": get_game_title(item),
                    "author": item.name,
                }
            )

    return sorted(games, key=lambda x: x["title"].casefold())


@app.route("/")
def index():
    """Главная страница со списком игр"""
    try:
        games = get_games_list()
        if not games:
            return render_template("empty.html", config=app.config)

        return render_template("index.html", games=games, config=app.config)
    except Exception as e:
        logger.error(f"Ошибка в index: {e}")
        return render_template("error.html", error=str(e)), 500


@app.route("/games/<game>/<path:filename>")
def serve_game(game: str, filename: str):
    """Отдает файлы игр с проверкой безопасности"""
    game_dir = app.config["GAMES_DIR"] / game
    if not game_dir.is_dir() or ".." in filename:
        return "Not Found", 404
    return send_from_directory(game_dir, filename)


@app.route("/assets/<path:filename>")
def serve_asset(filename: str):
    """Отдает статические файлы"""
    if ".." in filename:
        return "Not Found", 404
    return send_from_directory(app.config["ASSETS_DIR"], filename)


@app.context_processor
def inject_utilities():
    """Добавляет утилиты в контекст шаблонов"""

    def get_game_icon(game: str) -> str:
        icon_path = app.config["GAMES_DIR"] / game / "icon.png"
        return (
            url_for("serve_game", game=game, filename="icon.png")
            if icon_path.exists()
            else url_for("serve_asset", filename=app.config["DEFAULT_ICON"])
        )

    return {
        "get_game_icon": get_game_icon,
        "site_title": app.config["SITE_TITLE"],
        "github_url": app.config["GITHUB_URL"],
        "telegram_url": app.config["TELEGRAM_URL"],
    }


if __name__ == "__main__":
    app.run(
        host="localhost", port=8000, debug=False
    )  # В production debug=False!
