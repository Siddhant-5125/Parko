from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ParkingAreaViewSet,ParkingSlotsViewSet,BookingViewSet,scan_booking


router = DefaultRouter()
router.register(r'parking-area',ParkingAreaViewSet)
router.register(r'parking-slots',ParkingSlotsViewSet)
router.register(r'booking',BookingViewSet)

urlpatterns = [
    path('',include(router.urls)),
    path('scan/<int:booking_id>/', scan_booking, name='scan_booking')
]