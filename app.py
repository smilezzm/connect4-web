import logging
from pathlib import Path

import streamlit as st

from bot_bundle import bundle, search_lock


ROOT = Path(__file__).resolve().parent
LOG = logging.getLogger(__name__)


def new_game(rules, first=1, revision=0):
    return {
        "board": rules.new_board(),
        "first": first,
        "revision": revision,
        "last": None,
        "moves": 0,
        "bot": None,
        "error": "",
    }


def place(rules, game, column, player):
    board = rules.play_move(game["board"], column, player)
    row = next(row for row in range(6) if board[row, column] != 0)
    game.update(board=board, last=[row, column], moves=game["moves"] + 1)


def handle_action(bundle):
    request = st.session_state.arena.action
    game = st.session_state.match
    if not isinstance(request, dict) or request.get("revision") != game["revision"]:
        return

    rules = bundle.rules
    kind = request.get("type")
    revision = game["revision"] + 1
    if kind == "restart" and type(request.get("first")) is int and request["first"] in (-1, 1):
        next_game = new_game(rules, request["first"], revision)
    elif kind == "drop" and type(request.get("column")) is int:
        column = request["column"]
        if rules.game_result(game["board"])[0] or column not in rules.legal_moves(game["board"]):
            return
        next_game = dict(game, revision=revision, error="")
        place(rules, next_game, column, 1)
    else:
        return

    needs_bot = kind == "drop" or next_game["first"] == -1
    if needs_bot and not rules.game_result(next_game["board"])[0]:
        try:
            with search_lock:
                if next_game["bot"] is None:
                    next_game["bot"] = bundle.bot_class({"seed": 2026})
                column = next_game["bot"].act({
                    "game": "connect4",
                    "board": next_game["board"],
                    "player": -1,
                    "legal_actions": rules.legal_moves(next_game["board"]),
                })
                place(rules, next_game, column, -1)
        except Exception:
            LOG.exception("The bundled bot failed to move")
            game.update(revision=revision, bot=None, error="The bot couldn’t move. Please try again.")
            return

    st.session_state.match = next_game


def winning_cells(rules, board, winner):
    flat_board = board.reshape(-1)
    cells = {int(cell) for line in rules.LINES if (flat_board[line] == winner).all() for cell in line}
    return [divmod(cell, 7) for cell in sorted(cells)]


st.set_page_config(page_title="Connect Four | Play the Bot", page_icon="🟡", layout="wide")
st.html("""
<style>
    .stApp {background: #f4f2ea;}
    .stMainBlockContainer {max-width: 1120px; padding: 32px 36px 24px;}
    [data-testid="stHeader"] {background: transparent; height: 0;}
    @media (max-width: 640px) {.stMainBlockContainer {padding: 19px 16px 24px;}}
</style>
""")

if "match" not in st.session_state:
    st.session_state.match = new_game(bundle.rules)

game = st.session_state.match
finished, winner = bundle.rules.game_result(game["board"])
component = st.components.v2.component(
    "connect_four_arena",
    html=(ROOT / "ui" / "board.html").read_text(encoding="utf-8"),
    css=(ROOT / "ui" / "board.css").read_text(encoding="utf-8"),
    js=(ROOT / "ui" / "board.js").read_text(encoding="utf-8"),
)
component(
    key="arena",
    data={
        "board": game["board"].tolist(),
        "first": game["first"],
        "moves": game["moves"],
        "revision": game["revision"],
        "last": game["last"],
        "error": game["error"],
        "legal": [] if finished else bundle.rules.legal_moves(game["board"]),
        "result": int(winner) if finished else None,
        "winning": winning_cells(bundle.rules, game["board"], winner) if winner else [],
    },
    on_action_change=lambda: handle_action(bundle),
)
