import psycopg2
from peewee import *

from config import DB_HOST, DB_PORT, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DATABASE

db = PostgresqlDatabase(POSTGRES_DATABASE, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD,
                        host=DB_HOST, port=DB_PORT)


class MyUser(Model):
    name = TextField()
    city = TextField(constraints=[SQL("DEFAULT 'Mumbai'")])
    age = IntegerField()

    class Meta:
        database = db
        db_table = 'MyUser'


def create_tables():
    with db:
        db.create_tables([MyUser])

