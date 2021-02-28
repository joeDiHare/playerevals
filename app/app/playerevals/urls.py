from django.urls import path

from . import views
from django.views.generic import TemplateView


app_name = 'playerevals'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:rid>/detail/', views.DetailView.as_view(), name='detail'),
    path('<str:rid>/vote/', views.vote, name='vote'),
    path('<str:reviewer>/done/', views.DoneView.as_view(), name='done'),
    path('collect/', views.dumpdb, name='dumpdb'),
    path('lost/', views.LostView.as_view(), name='lost'),
]
