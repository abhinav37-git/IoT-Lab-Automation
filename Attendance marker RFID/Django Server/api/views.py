from rest_framework.views import APIView
from django.http import JsonResponse
from .models import *
from django.utils.timezone import localdate, localtime

errorParametersNotPresent = {"error": "parameters not present"}
errorDuplicateRecordPresent = {
    "error": "cannot add record",
    "reason": "duplicate record present",
}
successResult = {"result": "success"}


class DemoRecord(APIView):

    def post(self, request):

        cardID = request.POST.get("cardID")
        scannerID = request.POST.get("scannerID")

        # if cardID is None or scannerID is None:
        #     return JsonResponse(errorParametersNotPresent)

        print(f"CardID: {cardID}\nScannerID: {scannerID}\n\n")
        return JsonResponse({"result": "success"})


class AddRecord(APIView):

    def post(self, request):
        cardID = request.POST.get("cardID")
        scannerID = request.POST.get("scannerID")

        if cardID is None or scannerID is None:
            return JsonResponse(errorParametersNotPresent)
        record = AttendanceRecord()
        record.cardID = cardID[1:]
        record.scannerID = scannerID
        # try:
        # print(f"{cardID} {scannerID} scanned")
        # print(f"{len(cardID[1:])} {cardID[1:]} {len(studentQ[0].cardID)} {studentQ[0].cardID} {cardID[1:] == studentQ[0].cardID}")
        studentQuery = Student.objects.filter(cardID=record.cardID)
        scannerRoomQuery = ScannerRoom.objects.filter(scannerID=scannerID)
        if len(studentQuery) > 0 and len(scannerRoomQuery) > 0:
            # TODO: Add logic to ensure student has scanned card in correct room
            # TODO: Send data to CUIMS backend to mark attendance of the student for respective lecture
            # Saving record of AttendanceRecord in Local DB
            print("Record Saved")
            record.save()
        return JsonResponse(successResult)
        # except:
        #     return JsonResponse(errorDuplicateRecordPresent)


class UpdatePersonCount(APIView):

    def post(self, request):
        people_count = request.POST.get("count")

        if people_count is None:
            return JsonResponse(errorParametersNotPresent)

        try:
            record = PersonCountData(count=people_count)
            record.save()
            return JsonResponse(successResult)
        except Exception as e:  # Add more specific error handling if needed
            return JsonResponse({"error": str(e)})