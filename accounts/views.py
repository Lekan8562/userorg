from django.db import transaction
from django.contrib.auth import authenticate

from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from organization.models import Organisation

from .models import User
from .serializers import UserSerializer, OrganisationSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        org_name = f"{user.firstName}'s Organisation"
        Organisation.objects.create(name=org_name, users=[user])
        token = RefreshToken.for_user(user)
        response_data = {
            'status': 'success',
            'message': 'Registration successful',
            'data': {
                'accessToken': str(token.access_token),
                'user': UserSerializer(user).data
            }
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            token = RefreshToken.for_user(user)
            response_data = {
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'accessToken': str(token.access_token),
                    'user': UserSerializer(user).data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        return Response({'status': 'Bad request', 'message': 'Authentication failed', 'statusCode': 401}, status=status.HTTP_401_UNAUTHORIZED)

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'userId'

class OrganisationListView(generics.ListAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return user.organisations.all()

class OrganisationDetailView(generics.RetrieveAPIView):
    queryset = Organisation.objects.all()
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'orgId'

class OrganisationCreateView(generics.CreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(users=[self.request.user])

class AddUserToOrganisationView(generics.GenericAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        orgId = self.kwargs.get('orgId')
        userId = request.data.get('userId')
        try:
            organisation = Organisation.objects.get(orgId=orgId)
            user = User.objects.get(userId=userId)
            organisation.users.add(user)
            return Response({'status': 'success', 'message': 'User added to organisation successfully'}, status=status.HTTP_200_OK)
        except (Organisation.DoesNotExist, User.DoesNotExist):
            return Response({'status': 'Bad request', 'message': 'Invalid organisation or user ID', 'statusCode': 400}, status=status.HTTP_400_BAD_REQUEST)
