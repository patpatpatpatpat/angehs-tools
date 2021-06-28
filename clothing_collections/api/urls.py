from django.urls import path, include


from rest_framework import routers
from . import views

app_name = "collections"

router = routers.DefaultRouter()

router.register("batches", views.BatchViewSet, basename="batches")

urlpatterns = [
    path("", include(router.urls)),
]