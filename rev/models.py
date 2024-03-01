from rev.config import db
from peewee import Model, CharField, DateTimeField, AutoField, FloatField, TextField, ForeignKeyField, BooleanField
from rev.helpers import current_datetime


class Base(Model):
    created = DateTimeField(default=current_datetime())
    updated = DateTimeField(default=current_datetime())

    class Meta:
        database = db
        legacy_table_names = False


class Users(Base):
    id = AutoField(unique=True, primary_key=True)
    eid = CharField(max_length=100)
    username = CharField(max_length=300, unique=True, null=False)
    password = CharField(max_length=700, null=False)
    first_name = CharField(max_length=300)
    last_name = CharField(max_length=300)
    email = CharField(max_length=300, null=False)
    level = CharField(max_length=50, default='user')
    account = CharField(max_length=300)
    superadmin = BooleanField()
    status = BooleanField()


class Checking(Base):
    id = AutoField(unique=True, primary_key=True)
    users = ForeignKeyField(Users, backref='checking')
    checkin = DateTimeField(null=False)
    checkout = DateTimeField(null=False)
    status = CharField(max_length=10)
    total_hours = FloatField(default=0.0)
    eod = TextField(null=True)


class Breaks(Base):
    id = AutoField(unique=True, primary_key=True)
    users = ForeignKeyField(Users, backref='breaks')
    checking = ForeignKeyField(Checking, backref='breaks')
    start = DateTimeField(null=False)
    end = DateTimeField(null=False)
    status = CharField(max_length=10)
    mode = CharField(max_length=20)
    total_hours = FloatField(default=0.0)


class Reports(Base):
    id = AutoField(primary_key=True)
    users = ForeignKeyField(Users, backref='reports')
    title = CharField(max_length=500)
    severity = CharField(max_length=100)
    details = TextField()
    resolved = BooleanField()
    remarks = TextField()
    