# from django.urls import path
# from .views import *

# urlpatterns = [
#     path("addrecord", AddRecord.as_view()),
#     path("demo", DemoRecord.as_view()),
#     path("updatepersoncount", UpdatePersonCount.as_view()),
# ]
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('demo-record/', views.DemoRecord.as_view(), name='demo-record'),
    path('add-record/', views.AddRecord.as_view(), name='add-record'),
    path('update-person-count/', views.UpdatePersonCount.as_view(), name='update-person-count'),
]