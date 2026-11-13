from rest_framework import generics, permissions, viewsets
from .models import Address
from .serializers import RegisterSerializer, ProfileSerializer, AddressSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    def get_object(self): return self.request.user

class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self): return Address.objects.filter(user=self.request.user)
    def perform_create(self, serializer): serializer.save(user=self.request.user)
