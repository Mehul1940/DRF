from django.urls import path , include
from Home.views import *
from  rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"people", peopleViewSet, basename='people')
urlpatterns = router.urls

urlpatterns = [
    path("",include(router.urls)),
    path("index/",index),
    path('register/',RegisterAPI.as_view()),
    path('login/',LoginAPI.as_view()),
    path("login/",login),
    path('persons/', PersonAPI.as_view())
]
