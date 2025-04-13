import os
from flask import Flask, render_template, send_from_directory, url_for
from pathlib import Path

app = Flask(__name__)
app.config['ROOT_DIR'] = Path(app.root_path)
app.config['GAMES_DIR'] = app.config['ROOT_DIR'] / 'games'
app.config['ASSETS_DIR'] = app.config['ROOT_DIR'] / 'assets'
app.config['DEFAULT_ICON'] = 'default-game-icon.png'
app.config['SITE_TITLE'] = 'Игровой портал'

def get_games_list():
    games_dir = app.config['GAMES_DIR']
    if not games_dir.is_dir():
        raise FileNotFoundError("Директория с играми не найдена")

    games = []
    for item in games_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            games.append(item.name)

    return sorted(games, key=str.casefold) if games else []

def get_icon_path(game_name):
    icon_path = games_dir / game_name / 'icon.png'
    return icon_path if icon_path.exists() else None

@app.route('/')
def index():
    try:
        games = get_games_list()
        if not games:
            raise ValueError("На данный момент игр нет в каталоге")

        return render_template('index.html',
                            games=games,
                            config=app.config)
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/games/<game>/<path:filename>')
def serve_game(game, filename):
    return send_from_directory(
        app.config['GAMES_DIR'] / game,
        filename
    )

@app.route('/assets/<path:filename>')
def serve_asset(filename):
    return send_from_directory(
        app.config['ASSETS_DIR'],
        filename
    )

@app.context_processor
def inject_utilities():
    def get_game_icon(game):
        icon_path = app.config['GAMES_DIR'] / game / 'icon.png'
        if icon_path.exists():
            return url_for('serve_game', game=game, filename='icon.png')
        return url_for('serve_asset', filename=app.config['DEFAULT_ICON'])

    return dict(
        get_game_icon=get_game_icon,
        site_title=app.config['SITE_TITLE']
    )

if __name__ == '__main__':
    app.run(debug=True)