from .models import ParkingArea, ParkingSlots, Booking
from rest_framework import serializers
from parkinguser.serializers import UserSerializer,ParkingUserSerializer


class ParkingAreaSerializer(serializers.ModelSerializer):
    owner = ParkingUserSerializer(read_only=True)
    parking_slots = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    available_slots = serializers.SerializerMethodField()
    class Meta:
        model = ParkingArea
        fields = ['id', 'latitude', 'longitude', 'owner', 'parking_slots', 'available_slots','owner']
        
    def create(self, validated_data):
        owner = validated_data.pop('owner')
        parking_area = ParkingArea.objects.create(owner=owner, **validated_data)
        return parking_area

    def get_available_slots(self, obj):
        return ParkingSlots.objects.filter(parking_area=obj, available=True, reserved=False).count()

        

class ParkingSlotsSerializers(serializers.ModelSerializer):
    parking_area = serializers.PrimaryKeyRelatedField(queryset=ParkingArea.objects.all())
    booking = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )

    class Meta:
        model = ParkingSlots
        fields = ['id', 'parking_area', 'available', 'reserved', 'reserved_for_start', 'reserved_for_end', 'booking']


class BookingSerializer(serializers.ModelSerializer):
    slot = serializers.PrimaryKeyRelatedField(queryset=ParkingSlots.objects.all())
    user = UserSerializer(read_only=True)
    qr_code = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'slot', 'req_time_start', 'req_time_end', 'user', 'qr_code', 'status','phone_number']
    def get_qr_code(self, obj):
        if obj.qr_code:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.qr_code.url)
            else:
                return obj.qr_code.url
        return None
        
