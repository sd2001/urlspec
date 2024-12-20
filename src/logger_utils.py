import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO,  # Setting log level globally
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(), logging.FileHandler('app.log')])
