import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Hello, my name is Rudolf and I have a secret...'
    ITEMS_PER_PAGE = 40
    MAX_ITEMS_RETURNED = 5000
    INDEX = 'bi'
    ELASTICSEARCH_URL = ['http://localhost:9200']

