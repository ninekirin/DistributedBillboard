import logging

# 日志系统设置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# filename='billboard.log', 
def log_action(action):
    logging.info(action)

def log_error(error):
    logging.error(error)

def log_warning(warning):
    logging.warning(warning)

def log_debug(debug):
    logging.debug(debug)

def log_critical(critical):
    logging.critical(critical)

def log_exception(exception):
    logging.exception(exception)