import logging
import json
from datetime import datetime

def getConfig(logger):
    return fromJsonFile("jsons/config.json", logger)

def setupHandler():
    filename = datetime.now().strftime("%Y%m%d%H%M%S")
    handler = logging.FileHandler(filename=f'logs\{filename}.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    return handler

def setupLogger(handler, name="discord", level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

def toJsonFile(filename, dictJson, logger):
    try:
        with open(filename, 'w', encoding="utf8") as f:
            json.dump(dictJson, f, default=lambda o: o.__dict__, sort_keys=True, indent=4)
        logger.info(f'Success dump to {filename}')
        return True
    except Exception as e:
        logger.error(str(e))
        return False

def fromJsonFile(filename, logger):
    try:
        with open(filename, 'r', encoding="utf8") as f:
            container = json.load(f)
        logger.info(f'Success load from {filename}')
        return container
    except Exception as e:
        logger.error(str(e))
        return dict()