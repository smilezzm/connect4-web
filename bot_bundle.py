"""Load the bundled course export without editing its code or weights."""

import importlib
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Lock
from zipfile import ZipFile


# The engine measures process CPU time, so searches must run serially.
search_lock = Lock()


class BotBundle:
    def __init__(self):
        assets = Path(__file__).resolve().parent / "bot_assets"
        self.directory = TemporaryDirectory(prefix="connect4-bot-")
        root = Path(self.directory.name)
        with ZipFile(assets / "code.zip") as archive:
            archive.extractall(root)
        model_dir = root / "models"
        model_dir.mkdir()
        shutil.copyfile(assets / "model.pt", model_dir / "model.pt")

        # The export expects flat imports such as `from mcts import search`.
        sys.path.insert(0, str(root))
        try:
            self.bot_class = importlib.import_module("strategy").Bot
            self.rules = importlib.import_module("support.game")
            importlib.import_module("model")
            importlib.import_module("root_ensemble")
        finally:
            sys.path.remove(str(root))


bundle = BotBundle()
