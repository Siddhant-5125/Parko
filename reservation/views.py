import os
import uuid
from django.conf import settings
from django.shortcuts import render, get_object_or_404
import qrcode
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
import math
from .models import ParkingSlots, ParkingArea, Booking, ParkingUser
from .serializers import ParkingAreaSerializer, ParkingSlotsSerializers, BookingSerializer
from rest_framework import viewsets,serializers
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from datetime import time


def haversine(ulat, ulong, slat, slong):
    ulat = math.radians(ulat)
    ulong = math.radians(ulong)
    slat = math.radians(slat)
    slong = math.radians(slong)

    dlat = slat - ulat
    dlong = slong - ulong

    a = math.sin(dlat / 2) ** 2 + math.cos(ulat) * math.cos(slat) * math.sin(dlong / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = 6371 * c
    return distance


class ParkingAreaViewSet(viewsets.ModelViewSet):
    queryset = ParkingArea.objects.all()
    serializer_class = ParkingAreaSerializer


    def create(self, request, *args, **kwargs):
        owner_id = request.data.get('owner_id')

        if not owner_id:
            return Response({"error": "The owner_id field is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            parking_user = ParkingUser.objects.get(id=owner_id)
        except ParkingUser.DoesNotExist:
            return Response({"error": "The specified owner_id is not associated with a ParkingUser."}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        if 'owner_id' in data:
            data.pop('owner_id')
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        parking_area = serializer.save(owner=parking_user)          
        self.create_parking_slots_for_area(parking_area)

        return Response(self.get_serializer(parking_area).data, status=status.HTTP_201_CREATED)

    def create_parking_slots_for_area(self, parking_area):
        try:
            total_slots = parking_area.owner.total_slots

            parking_slots = [
                ParkingSlots(parking_area=parking_area, available=True, reserved=False)
                for _ in range(total_slots)
            ]
            ParkingSlots.objects.bulk_create(parking_slots)

            return f"{total_slots} parking slots have been successfully created for ParkingArea {parking_area.id}."

        except Exception as e:
            raise ValueError(f"An error occurred while creating parking slots: {str(e)}")

    @action(detail=False, methods=['get'], url_path ='nearby')
    def nearby(self, request):
        lat = request.query_params.get('user-lat')
        long = request.query_params.get('user-long')
        
        if lat is None or long is None:
            return Response({"error": "Please provide the latitude and longitude as query parameters"}, status=400)
        
        try:
            lat = float(lat)
            long = float(long)
        except ValueError:
            return Response({"error": "Invalid latitude and longitude must be numbers"}, status=400)
        

        parking_areas = self.get_queryset()
        
        results = []
        for area in parking_areas:

            distance = haversine(lat, long, area.latitude, area.longitude)
            results = []
        for area in parking_areas:
            distance = haversine(lat, long, area.latitude, area.longitude)

            available_slots_count = ParkingSlots.objects.filter(
                parking_area=area,
                available=True,
                reserved=False
            ).count()

            if available_slots_count > 0:
                parking_user = area.owner
                parking_user_data = {
                    "id": parking_user.id,
                    "name": parking_user.user.name,
                    "phone": parking_user.user.phone,
                    "email": parking_user.user.email,
                    "parking_name": parking_user.parking_name,
                    "address": parking_user.address,
                    "hourlyRate": parking_user.hourlyRate,
                    "openingHours": parking_user.openingHours,
                    "dailyRate": parking_user.dailyRate,
                    "monthlyRate": parking_user.monthlyRate,
                    "rating": parking_user.rating,
                    "image_url": parking_user.image_url,
                    "availableTypes": parking_user.availableTypes,
                    "description": parking_user.description,
                }

                results.append({
                    'id': area.id,
                    'latitude': area.latitude,
                    'longitude': area.longitude,
                    'available_slots': available_slots_count,
                    'distance': distance,
                    'parking_user': parking_user_data  # Include ParkingUser data
                })

        results = sorted(results, key=lambda x: x['distance'])
        return Response(results)

    @action(detail=True, methods=['get'], url_path='slots')
    def get_slots(self, request, pk=None):
        parking_area = self.get_object()
        slots = ParkingSlots.objects.filter(parking_area=parking_area)
        serializer = ParkingSlotsSerializers(slots, many=True)
        response_data = {
            'parking_area_id' : parking_area.id,
            'total_slots' : parking_area.owner.total_slots,
            "avaiilable_slots" : slots.filter(available=True, reserved=False).count(),
            "levels": parking_area.owner.levels,
            'slots': serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)

class ParkingSlotsViewSet(viewsets.ModelViewSet):
    queryset = ParkingSlots.objects.all()
    serializer_class = ParkingSlotsSerializers


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def handle_parking_slot_reservation(self, parking_slot_id, req_time_start, req_time_end, current_user):
        try:
            if req_time_start is None:
                req_time_start = time(0, 0, 0)
            if req_time_end is None:
                req_time_end = time(0, 0, 0)
            req_time_start = time.fromisoformat(req_time_start)
            req_time_end = time.fromisoformat(req_time_end)

            parking_slot = ParkingSlots.objects.get(id=parking_slot_id)

            if parking_slot.reserved:
                if (
                    (req_time_start <= parking_slot.reserved_for_start <= req_time_end) or
                    (req_time_start <= parking_slot.reserved_for_end <= req_time_end)
                ):
                    raise ValidationError("Slot has been already booked for the requested time range.")
                else:
                    raise ValidationError("The slot is already reserved for a different time range.")
            else:
                parking_slot.reserved = True
                parking_slot.reserved_for_start = req_time_start
                parking_slot.reserved_for_end = req_time_end
                parking_slot.save()

                booking = Booking.objects.create(
                    user=current_user,
                    slot=parking_slot,
                    req_time_start=req_time_start,
                    req_time_end=req_time_end,
                    status='booked'  # Set initial status
                )

                # Generate QR code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr_data = f"http://127.0.0.1:8000/reservation/scan/{booking.id}"
                qr.add_data(qr_data)
                qr.make(fit=True)

                # Create QR code image
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # Create media directory if it doesn't exist
                media_root = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
                os.makedirs(media_root, exist_ok=True)
                
                # Generate unique filename
                filename = f"booking_qr_{booking.id}_{uuid.uuid4().hex[:6]}.png"
                file_path = os.path.join(media_root, filename)
                
                # Save QR code image
                qr_image.save(file_path)
                
                # Update booking with QR code path
                booking.qr_code = f"qrcodes/{filename}"
                booking.save()

                return booking.id                
            
        except Exception as e:
            raise ValidationError(f"An error occurred: {str(e)}")


    def create(self, request, *args, **kwargs):
        parking_slot_id = request.data.get('slot')
        req_time_start = request.data.get('req_time_start')
        req_time_end = request.data.get('req_time_end')
        # qr_code = request.data.get('qr_code')
        # status = request.data.get('status')

        if not parking_slot_id or not req_time_start or not req_time_end:
            return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

        # print(request.data)
        try:
            result = self.handle_parking_slot_reservation(
                parking_slot_id=int(parking_slot_id),
                req_time_start=req_time_start,
                req_time_end=req_time_end,
                current_user=request.user,
                # qr_code = qr_code,
                # status = status
            )
            return Response({"message": result}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def scan_booking(request, booking_id):
    # booking_id = request.data.get('booking_id')
    
    if not booking_id:
        return Response({'error': 'Booking ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        booking = get_object_or_404(Booking, id=booking_id)
        
        if booking.status == 'booked':
            booking.status = 'entry'
            message = 'Booking status changed from Booked to Entry'
        elif booking.status == 'entry':
            booking.status = 'exit'
            parking_slot = booking.slot
            parking_slot.reserved = False
            parking_slot.save()
            message = 'Booking status changed from Entry to Exit'
        else:
            return Response({'error': 'Booking has already been completed'}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        booking.save()
        return Response({
            'message': message,
            'booking_id': booking.id,
            'status': booking.status
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)