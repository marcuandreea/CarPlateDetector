from pathlib import Path

from dotenv import load_dotenv


def load_env_file(env_path: str | Path | None = None) -> None:
    # Incarca variabilele din .env fara sa suprascrie valorile deja setate in consola.
    path = Path(env_path) if env_path else Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(dotenv_path=path, override=False)


load_env_file()

# Configuratie generala pentru aplicatie
MAX_PARKING_SPACES = 100
