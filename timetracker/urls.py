from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index),
    path('add-description',views.addDescription,name="addDescription"),
    path('remove-description',views.removeDescription,name="removeDescription"),
    path('get_description/<slug:hour_id>',views.getDescription,name="getDescription"),
    path('get-particular-date/<slug:day>/<slug:month>',views.get_particular_date,name="get_particular_date"),
    path('add-task',views.add_task,name="addtask"),
    path('get-tasks/<slug:day>/<slug:month>',views.get_tasks,name="get_tasks"),
    path('delete-task',views.delete_task,name="delete_tasks"),
    path('get-all-task-date',views.getAllTaskDate,name="getAllTaskDate"),
    path('get-all-day-description-date',views.getAllDayDescriptionDate,name="getAllDayDescriptionDate"),
    path('update-task',views.update_task,name="update_task"),
    path('autosuggestion',views.autosuggestion,name="autosuggestion")
]
