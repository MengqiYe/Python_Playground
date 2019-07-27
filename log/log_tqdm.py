import logging
import multiprocessing
import time
import colorlog
from tqdm import tqdm

class TqdmHandler(logging.StreamHandler):
    def __init__(self):
        logging.StreamHandler.__init__(self)

    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)


def compute(i):
    time.sleep(.5)
    return i**2

if __name__ == "__main__":
    logger = colorlog.getLogger("SQUARE")
    logger.setLevel(logging.DEBUG)
    handler = TqdmHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(name)s | %(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%d-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'white',
            'SUCCESS:': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white'},))

    logger.addHandler(handler)
    pool = multiprocessing.Pool()
    try:
        for square in tqdm(pool.imap_unordered(compute, range(100)), total=100):
            logger.debug(str(square))

    except KeyboardInterrupt:
        logging.warning("got Ctrl+C")
    finally:
        pool.terminate()
        pool.join()