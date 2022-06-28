```py
import sys, logging

client_logger = logging.getLogger("nextcord.client")
state_logger = logging.getLogger("nextcord.state")

FORMAT = "[\{asctime\}][\{filename\}][\{lineno:3\}][\{funcName\}][\{levelname\}] \{message\}"
formatter = logging.Formatter(FORMAT, style="\{")

console_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("latest.log", mode="w")

console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

client_logger.addHandler(console_handler)
state_logger.addHandler(console_handler)

client_logger.addHandler(file_handler)
state_logger.addHandler(file_handler)

client_logger.setLevel(logging.DEBUG)
state_logger.setLevel(logging.DEBUG)
```