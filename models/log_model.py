import logging

# 日志系统设置
logging.basicConfig(filename='billboard.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_action(action):
    logging.info(action)