from other.bug_trap import bug_trap
import configparser

config = configparser.ConfigParser()
config.read("other/conf.ini")

try:
    APP_IP = config['APP']['IP']
    APP_DEBUG = bool(config['APP']['DEBUG'])
    APP_DJANGO_IP = config['APP']['DJANGO_IP']
    APP_DJANGO_PORT = config['APP']['DJANGO_PORT']

    VK_USER_TOKEN = config['VK']['USER_TOKEN']
    VK_GROUP_ID = int(config['VK']['GROUP_ID'])
    VK_USER_ID = int(config['VK']['USER_ID'])
    VK_ALBUM_ID = int(config['VK']['ALBUM_ID'])
except Exception:
    bug_trap()
