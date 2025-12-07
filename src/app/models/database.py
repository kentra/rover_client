from peewee import *
import datetime

db = SqliteDatabase("my_database.db")


class BaseModel(Model):
    class Meta:
        database = db


class SystemStats(BaseModel):
    username = CharField(unique=True)
    cpu_temp = FloatField()
    cpu_usage = FloatField()
    ram_usage = FloatField()
    disk_usage = FloatField()


class RoverState(BaseModel):
    is_connected = BooleanField(default=False)
    is_driving = BooleanField(default=False)
    is_armed = BooleanField(default=False)
    mode = CharField(null=True)
    camera_online = BooleanField(default=False)


class EnvironmentSensorsState(BaseModel):
    humidity = FloatField(null=True)
    pressure = FloatField(null=True)
    temperature = FloatField(null=True)


# db.connect()
# db.create_tables([User, Tweet])
