from datetime import datetime

from peewee import (DateTimeField, IntegerField, TextField, BooleanField,
                    ForeignKeyField, AutoField, PostgresqlDatabase, Model)

from config import (DB_HOST, DB_PORT, POSTGRES_USERNAME, POSTGRES_PASSWORD,
                    POSTGRES_DATABASE, KEYS_COUNT)

db = PostgresqlDatabase(POSTGRES_DATABASE, user=POSTGRES_USERNAME,
                        password=POSTGRES_PASSWORD, host=DB_HOST, port=DB_PORT)


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


def create_new_user_on_start(tg_id, name):
    Users.create(
        tg_id=tg_id,
        name=name,
        is_approved=False,
        keys_count=KEYS_COUNT,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def get_user(tg_id) -> Users:
    return Users.select().where(Users.tg_id == tg_id).get()


def approve_user(user_id):
    Users.update(is_approved=True).where(Users.id == user_id).execute()


def get_users_for_approve() -> list[Users]:
    return Users.select().where(Users.is_approved == False)


def get_user_keys(tg_id) -> list[Keys]:
    return Keys.select().join(Users).where(Keys.user.tg_id == tg_id)


def create_key(tg_id, key_name, key_id):
    Keys.create(
        key_id=key_id,
        key_name=key_name,
        user=Users.select().where(Users.tg_id == tg_id).get(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


def change_keys_count(tg_id, key_count):
    Users.update(keys_count=key_count).where(Users.tg_id == tg_id).execute()


def delete_key(key_id):
    Keys.delete().where(Keys.key_id == key_id).execute()
