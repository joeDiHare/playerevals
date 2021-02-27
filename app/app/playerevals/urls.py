from django.urls import path

from . import views

app_name = 'playerevals'
urlpatterns = [
    path('<str:rid>/vote/', views.vote, name='vote'),
    path('<str:rid>/detail/', views.DetailView.as_view(), name='detail'),
    path('<str:reviewer>/completed/', views.CompletedView.as_view(), name='completed'),
    
]