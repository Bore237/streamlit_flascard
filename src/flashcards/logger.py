import logging
import logging.config
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "application.log"

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | "
        "%(levelname)-8s | "
        "%(name)s | "
        "%(filename)s:%(lineno)d | "
        "%(funcName)s()\n\n"
        "%(message)s\n"
    ),
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
    ],
)

def get_log(name):
    return logging.getLogger(name)


def process_data():
    logger = get_log(__name__)
    logger.debug("Début du traitement des données")

    try:
        logger.info("Démarrage du traitement")

        result = 100 / 2

        logger.info("Traitement terminé avec succès")
        logger.debug("Résultat : %s", result)

        return result

    except Exception:
        logger.exception("Erreur pendant le traitement")
        raise


if __name__ == "__main__":
    process_data()