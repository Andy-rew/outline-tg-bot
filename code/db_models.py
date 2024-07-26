import psycopg2
from peewee import (DateTimeField, IntegerField, TextField, BooleanField, ForeignKeyField, AutoField,
                    PostgresqlDatabase, Model)

from config import DB_HOST, DB_PORT, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_DATABASE

db = PostgresqlDatabase(POSTGRES_DATABASE, user=POSTGRES_USERNAME, password=POSTGRES_PASSWORD,
                        host=DB_HOST, port=DB_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    id = AutoField()
    tg_id = TextField(unique=True)
    name = TextField()
    is_approved = BooleanField(default=False)
    keys_count = IntegerField(default=0)
    created_at = DateTimeField()
    updated_at = DateTimeField()


class Keys(BaseModel):
    id = AutoField()
    key_id = TextField(unique=True)
    key_name = TextField()
    user = ForeignKeyField(Users, field='id')
    created_at = DateTimeField()
    updated_at = DateTimeField()


def create_tables():
    with db:
        db.create_tables([Users, Keys])
