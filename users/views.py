from rest_framework.views import APIView
from rest_framework import response
from rest_framework import status
from .serializer import UserSerializer, UpdateUserSerializer
from .models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


@api_view(["POST"])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    requested_role = data.get("role", "USER")
    if requested_role == "ADMIN" and not request.user.is_staff:
        return response.Response(
            {"error": "Only admins can create admin users"},
            status=status.HTTP_403_FORBIDDEN,
        )
    User.objects.create_user(
        username=data["username"],
        password=data["password"],
        email=data["email"],
        role=requested_role,
    )

    return response.Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])   
def create_admin(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    User.objects.create_user(
        username=data["username"],
        password=data["password"],
        email=data["email"],
        role=data["role"],
    )

    return response.Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request):
    user = request.user

    serializer = UserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return response.Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_users(request):
    data = User.objects.all()
    persons = UserSerializer(data, many=True)
    return response.Response(persons.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_user(request, id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return response.Response(
            {"error": "User not found"},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = UserSerializer(user)
    return response.Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def delete_user(request, id):
    try:
        user = User.objects.get(id = id)
        user.delete()
        return response.Response({"Deleted successfully"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return response.Response(
            {"error": "User not found"},
            status = status.HTTP_200_OK
        )
        
