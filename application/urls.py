from django.urls import path 
from application.views import home,about,add_note,delete_note,ai_agent
urlpatterns=[
    path('home/',home,name='home'),
    path('about/',about,name='about'),
    path('add_note/',add_note,name='add_note'),
    path('delete_note/<int:note_id>',delete_note,name='delete_note'),
    path('ai_agent/',ai_agent,name='ai_agent'),

]