from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import UserViewSets, ParkingUserViewSet

router = DefaultRouter()
router.register(r'user', UserViewSets)
router.register(r'parkinguser', ParkingUserViewSet)

urlpatterns = [
    path('',include(router.urls))
]