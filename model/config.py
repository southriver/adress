import os


class Config:
    # MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'demgood.mysql.pythonanywhere-services.com')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'demgood')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'Secur0t@$')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'demgood$demgoodDB')
    BEARER_TOKEN = os.environ.get('BEARER_TOKEN', 'Secur0t@$')

