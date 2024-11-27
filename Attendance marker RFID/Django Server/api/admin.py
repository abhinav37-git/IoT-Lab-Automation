from django.contrib import admin
from .models import *


class AttendanceRecordAdmin(admin.ModelAdmin):
    readonly_fields = ("createdAt",)


# Register your models here.


admin.site.register(AttendanceRecord, AttendanceRecordAdmin)
admin.site.register(Student)
admin.site.register(Room)
admin.site.register(ScannerRoom)
admin.site.register(Lecture)
admin.site.register(PersonCountData)
