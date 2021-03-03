from django.urls import path

from . import views
from django.views.generic import TemplateView


app_name = 'playerevals'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:rid>', views.EvalView.as_view(), name='eval'),
    path('<str:rid>/start', views.StartView.as_view(), name='start'),
    path('<str:rid>/thanks', views.ThanksView.as_view(), name='thanks'),
    path('<str:rid>/vote/', views.vote, name='vote'),
    path('<str:rid>/player/', views.PlayerView.as_view(), name='player'),
    path('<str:reviewer>/done/', views.DoneView.as_view(), name='done'),
    path('lost/', views.LostView.as_view(), name='lost'),
]
