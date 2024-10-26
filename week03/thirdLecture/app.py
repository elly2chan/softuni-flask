from flask import Flask
from decouple import config

app = Flask(__name__)


db_user = config('DB_USER')
db_password = config('DB_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{db_user}:{db_password}@localhost:5432/store'
