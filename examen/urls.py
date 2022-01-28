from django.urls import path, include
from . import views
from random import randint, choice


app_name = 'examen'
urlpatterns = [
    path('',views.home,name='home'),
    path('exam/<str:examen_id>',views.new_submit,name = 'submit'),
    path('submit_success/<str:alumno_id>',views.submit_success,name='submit_success'),
    path('submit_fail',views.submit_fail,name='submit_fail'),
    path('assignation/<str:examen_id>',views.assignation,name = 'assignation'),
    path('report/<str:examen_id>',views.exam_report,name = 'report'),
    path('sender/<str:examen_id>',views.sender,name = 'sender'),
    path('live_submit',views.live_submit,name='live_submit')
]