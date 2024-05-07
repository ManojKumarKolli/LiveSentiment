
from django.urls import path,include
from . import views

urlpatterns = [
   path('',views.home,name="home"),
   path('classify/', views.home, name='classify'),
   path('api/video-metrics/', views.video_metrics, name='video-metrics'),
   path('api/recommend-genre/', views.recommend_genre, name='recommend-genre'),
]