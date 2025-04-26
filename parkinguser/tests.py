# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework import status
# from rest_framework.test import APITestCase
# from .models import User, ParkingUser

# class JWTAuthenticationTestCase(APITestCase):
#     def setUp(self):
#         self.user_credentials = {
#             'username': 'testuser',
#             'password': 'testpassword'
#         }
#         self.user = User.objects.create_user(**self.user_credentials)

#     def test_jwt_authentication(self):
#         response = self.client.post('/api/token/', self.user_credentials)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('access', response.data)
#         self.assertIn('refresh', response.data)

#         access_token = response.data['access']
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
#         response = self.client.get('/api/protected/')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)