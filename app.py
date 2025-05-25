from flask import Flask, render_template, send_from_directory, url_for, request
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
    ASSETS_DIR=Path(__file__).parent / "static" / "assets",
    DEFAULT_ICON="default-game-icon.png",
    SITE_TITLE="Игровой портал от Sarcandi",
    PROJECT_NAME="IProject",
    PROJECT_GITHUB_URL="https://github.com/Sarcandi31/iproject",
    GITHUB_URL="https://github.com/Sarcandi",
    TELEGRAM_URL="https://t.me/sarcandi",
    TELEGRAM_ERROR_URL="https://t.me/m/3x674PdLY2Fi",
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
                    "author": item.name,
                }
            )

    return sorted(games, key=lambda x: x["title"].casefold()) if games else []


@app.route("/")
def index():
    """Главная страница со списком игр"""
    try:
        games = get_games_list()
        if not games:
            return render_template("empty.html", config=app.config)
        return render_template("index.html", games=games, config=app.config)
    except Exception as e:
        logger.error(f"Ошибка при загрузке основной страницы: {e}")
        return render_template("error.html", error=str(e)), 500


@app.route("/games/<game>/<path:filename>")
def serve_game(game: str, filename: str):
    """Отдает файлы игр с проверкой безопасности"""
    game_dir = app.config["GAMES_DIR"] / game
    if not game_dir.is_dir() or ".." in filename:
        return "Not Found", 404
    return send_from_directory(game_dir, filename)


@app.route("/css/<path:filename>")
def serve_css(filename):
    return send_from_directory("static/css", filename)


@app.route("/js/<path:filename>")
def serve_js(filename):
    return send_from_directory("static/js", filename)


@app.route("/img/<path:filename>")
def serve_img(filename):
    return send_from_directory("static/image", filename)


def is_mobile():
    user_agent = request.headers.get("User-Agent", "").lower()
    mobile_keywords = [
        "iphone",
        "android",
        "ipod",
        "blackberry",
        "windows phone",
    ]
    return any(keyword in user_agent for keyword in mobile_keywords)


@app.before_request
def block_mobile():
    # Разрешаем все запросы к статическим файлам (определяем по расширению)
    if "." in request.path and request.path.rsplit(".", 1)[1].lower() in {
        "css",
        "js",
        "png",
        "jpg",
        "jpeg",
        "gif",
        "ico",
        "svg",
        "woff",
        "woff2",
        "ttf",
        "eot",
    }:
        return None

    if is_mobile():
        return render_template("mobile.html"), 403

    return None


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(Exception)
def handle_all_errors(e):
    logger.error(f"Необработанная ошибка: {e}")
    return render_template("error.html", error="Что-то пошло не так"), 500


@app.template_global()
def get_game_icon(game: str) -> str:
    icon_path = app.config["GAMES_DIR"] / game / "icon.png"
    return (
        url_for("serve_game", game=game, filename="icon.png")
        if icon_path.exists()
        else url_for("serve_img", filename=app.config["DEFAULT_ICON"])
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=88, debug=True)
