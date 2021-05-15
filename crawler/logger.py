import os
import logging
import datetime

# Create custom logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create handlers
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), os.pardir, 'logs/otomoto_passanger_car_data_')) +
    str(datetime.date.today().strftime("%d_%m_%Y")) + ".log")

stream_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.INFO)

# Create and set formatters for handlers
stream_format = logging.Formatter(
    '%(name)s - %(levelname)s - %(message)s')
file_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(message)s')

stream_handler.setFormatter(stream_format)
file_handler.setFormatter(file_format)

# Add handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
