import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from const import LOG_FILE, LOG_FILE_BACKUP_COUNT, LOG_FILE_MAX_BYTES, LOG_LEVEL


class ConsoleFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        extra_data = getattr(record, "extra_data", None)
        if extra_data:
            message = f"{message} | {json.dumps(extra_data, default=str, ensure_ascii=False)}"
        return message


class JSONFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        extra_data = getattr(record, "extra_data", None)
        if extra_data:
            entry["extra_data"] = extra_data
        if record.exc_info and record.exc_info[0]:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

        console = logging.StreamHandler()
        console.setFormatter(ConsoleFormatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        ))
        logger.addHandler(console)

        if LOG_FILE:
            log_path = Path(LOG_FILE)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                str(log_path),
                maxBytes=LOG_FILE_MAX_BYTES,
                backupCount=LOG_FILE_BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setFormatter(JSONFormatter(datefmt="%Y-%m-%dT%H:%M:%S"))
            logger.addHandler(file_handler)

    return logger
