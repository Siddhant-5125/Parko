from rest_framework import serializers
from .models import User, ParkingUser
from reservation.models import ParkingArea, ParkingSlots, Booking

class UserSerializer(serializers.ModelSerializer):
    is_parking_owner = serializers.BooleanField(write_only=True, default=False)
    parking_name = serializers.CharField(write_only=True,required=False)
    total_slots = serializers.IntegerField(write_only=True, required=False)
    hourlyRate = serializers.FloatField(write_only=True, required=False)
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    dailyRate = serializers.FloatField(write_only=True, required=False)
    monthlyRate = serializers.FloatField(write_only=True, required=False)
    openingHours = serializers.CharField(write_only=True, required=False)
    description = serializers.CharField(write_only=True, required=False)
    levels = serializers.IntegerField(write_only=True, required=False)
    address = serializers.CharField(write_only=True, required=False)
    rating = serializers.FloatField(write_only=True, required=False)
    image_url = serializers.CharField(write_only=True, required=False)
    availableTypes = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username','name', 'email', 'password', 'is_parking_owner', 'parking_name', 'total_slots', 'hourlyRate', 'latitude', 'longitude', 'dailyRate', 'monthlyRate', 'openingHours', 'description', 'levels', 'address', 'rating', 'image_url','availableTypes']   
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        is_parking_owner = validated_data.pop('is_parking_owner',False)
        parking_user_data = {
            'parking_name': validated_data.pop('parking_name',""),
            'total_slots': validated_data.pop('total_slots', 0),
            'hourlyRate': validated_data.pop('hourlyRate', 0.0),
            'dailyRate': validated_data.pop('dailyRate', 0.0),
            'monthlyRate': validated_data.pop('monthlyRate', 0.0),
            'openingHours': validated_data.pop('openingHours', ""),
            'description': validated_data.pop('description', ""),
            'levels': validated_data.pop('levels', 1),
            'address': validated_data.pop('address', ""),
            'image_url': validated_data.pop('image_url', ""),
            'rating': validated_data.pop('rating', 4.5),
        }
        parking_area_data = {
            'latitude': validated_data.pop('latitude', 0.0),
            'longitude': validated_data.pop('longitude', 0.0),
        }

        print(validated_data)
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username = validated_data['username'],
            name = validated_data['name'],
            email = validated_data['email'],
            password= password
        )

        if is_parking_owner:
            parking_user = ParkingUser.objects.create(user=user, **parking_user_data)
            print(user)
            parking_area = ParkingArea.objects.create(owner=parking_user, **parking_area_data)
            self.create_parking_slots_for_area(parking_area)
            

        return user
    
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


class ParkingUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )

    class Meta:
        model = ParkingUser
        fields = ['id', 'user', 'user_id', 'parking_name', 'total_slots', 'hourlyRate', 'dailyRate', 'monthlyRate', 'openingHours', 'description', 'levels', 'address', 'rating', 'image_url', 'availableTypes']