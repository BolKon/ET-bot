from peewee import *


db = SqliteDatabase('users.db')


class User(Model):
    u_id = IntegerField()
    command = CharField()
    date = DateTimeField()
    city = CharField()
    currency = CharField(null=True)
    min_price = IntegerField(null=True)
    max_price = IntegerField(null=True)
    min_distance = FloatField(null=True)
    max_distance = FloatField(null=True)
    check_in = DateField()
    check_out = DateField()
    hotels = CharField()
    photos_list = CharField(null=True)
    photos_check = BooleanField()

    class Meta:
        database = db


with db:
    User.create_table()
