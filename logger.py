import logging
from logging.handlers import TimedRotatingFileHandler
import configparser
# Create the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)
config = configparser.ConfigParser()
config.read("conf.ini")

logpath = config.get("app", "logpath")

# Create a TimedRotatingFileHandler to log messages to a file
log_handler = TimedRotatingFileHandler(
    f"{logpath}gitmodule.log", 
    when="midnight", 
    interval=1, 
    backupCount=7
)

# Set a formatter for the log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(log_handler)

# You can also include a console handler if you want to see logs in the terminal.
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
#CHANGE in test
