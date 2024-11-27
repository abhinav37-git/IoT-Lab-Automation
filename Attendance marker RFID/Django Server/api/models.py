from django.db import models
from django.utils.timezone import localdate, localtime
import requests

roomIDMaxLen = 10
lectureIDMaxLen = 15
attendanceRecordMaxLen = 50
uidMaxLen = 15
cardIDMaxLen = 50
scannerIDMaxLen = 50
sectionMaxLen = 15
groupMaxLen = 3
blockMaxLen = 5
roomNoMaxLen = 5


class AttendanceRecord(models.Model):

    # def __init__(self, cardID, scannerID):
    #     self.cardID = cardID
    #     scannerID = scannerID

    def __str__(self):
        print("Models: ", len(self.cardID))
        studentQuery = Student.objects.filter(cardID=self.cardID)
        uid = "" if len(studentQuery) == 0 else studentQuery[0].uid
        return f"{self.id} {uid} {self.createdAt}"

    id = models.AutoField(primary_key=True)
    cardID = models.CharField(max_length=cardIDMaxLen, null=False)
    scannerID = models.CharField(max_length=scannerIDMaxLen, null=False)
    createdAt = models.DateTimeField(auto_now_add=True)


class Student(models.Model):

    def __str__(self):

        return f"{self.uid} {self.name}"

    uid = models.CharField(primary_key=True, max_length=uidMaxLen)
    cardID = models.CharField(null=False, max_length=cardIDMaxLen)
    name = models.TextField(max_length=50, null=False)
    age = models.IntegerField(null=False)
    section = models.CharField(max_length=sectionMaxLen, null=False)
    group = models.CharField(max_length=groupMaxLen, null=False)


class Room(models.Model):

    def __str__(self):
        return f"{self.block} {self.roomNo}"

    id = models.CharField(primary_key=True, max_length=roomIDMaxLen)
    block = models.CharField(max_length=blockMaxLen, null=False)
    roomNo = models.CharField(max_length=roomNoMaxLen, null=False)


class ScannerRoom(models.Model):

    def __str__(self):
        return f"Scanner: {self.scannerID} Room: {self.roomID}"

    scannerID = models.CharField(primary_key=True, max_length=scannerIDMaxLen)
    roomID = models.CharField(null=False, max_length=roomIDMaxLen)


class Lecture(models.Model):

    def __str__(self):
        return f"{self.section} ( {self.group} ) {self.day} {self.fromTime} - {self.toTime}"

    lectureID = models.CharField(primary_key=True, max_length=lectureIDMaxLen)
    roomID = models.CharField(max_length=roomIDMaxLen)
    section = models.CharField(null=False, max_length=sectionMaxLen)
    group = models.CharField(max_length=groupMaxLen, null=False)
    day = models.CharField(null=False, max_length=10)
    fromTime = models.TimeField(null=False)
    toTime = models.TimeField(null=False)


class PersonCountData(models.Model):

    def __str__(self):
        _datetime = self.timestamp.astimezone().strftime("%m/%d/%Y, %H:%M:%S")
        return f"Count: {self.count} at {_datetime}"

    count = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(default=localdate)
    time = models.TimeField(default=localtime)

#create a model for 