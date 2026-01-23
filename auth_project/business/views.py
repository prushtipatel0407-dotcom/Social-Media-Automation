from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import BusinessProfile
from .serializers import BusinessProfileSerializer

class BusinessProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = BusinessProfile.objects.filter(user=request.user).first()

        if not profile:
            return Response({"completed": False})

        return Response({
            "completed": True,
            "data": BusinessProfileSerializer(profile).data
        })

    def post(self, request):
        if BusinessProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Business profile already exists"},
                status=400
            )

        serializer = BusinessProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(
            {"message": "Business onboarding completed"},
            status=201
        )
