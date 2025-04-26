from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from .models import User, ParkingUser
from .serializers import UserSerializer,ParkingUserSerializer
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSets(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['get'],url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ParkingUserViewSet(viewsets.ModelViewSet):
    queryset = ParkingUser.objects.all()
    serializer_class = ParkingUserSerializer
    permission_classes = [permissions.IsAuthenticated] 