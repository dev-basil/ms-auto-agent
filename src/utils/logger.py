import logging
def logger(Errorcode:str ,description: str, ErrorlogType:str) -> logging.Logger:
    logger = logging.getLogger("sample-app")
    logger.info(f"{Errorcode}: {description}")
    return logger