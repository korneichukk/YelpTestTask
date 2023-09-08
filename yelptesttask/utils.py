import colorlog
import logging


# Colorful logging
class LoggingFormatter(colorlog.ColoredFormatter):
    def __init__(self):
        super().__init__(
            style="{",
            fmt=(
                "[{log_color}{levelname:^10}{reset}]"
                " -- {log_color}[{message}]{reset}"
                " -- {log_color}[{asctime}]{reset}"
                " -- {log_color}[{filename}:{lineno:d}]"
            ),
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )


handler = colorlog.StreamHandler()
handler.setFormatter(LoggingFormatter())

logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)
