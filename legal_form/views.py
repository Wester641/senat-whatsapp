# views.py
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from drf_spectacular.types import OpenApiTypes
import threading
import logging

from .models import ConsultationRequest, ServiceType
from .serializers import ConsultationRequestSerializer
from .services import TelegramService

logger = logging.getLogger(__name__)


@extend_schema(
    tags=['Consultation'],
    summary='Create consultation request',
    description='Create a new consultation request and send WhatsApp notification in background',
    request=ConsultationRequestSerializer,
    responses={
        201: ConsultationRequestSerializer,
        400: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Valid request',
            value={
                'name': 'Иван Иванов',
                'email': 'ivan@example.com',
                'phone': '+998901234567',
                'service_type': 'contracts',
                'comment': 'Нужна помощь с договором аренды'
            },
            request_only=True,
        ),
        OpenApiExample(
            'Successful response',
            value={
                'id': 1,
                'name': 'Иван Иванов',
                'email': 'ivan@example.com',
                'phone': '+998901234567',
                'service_type': 'contracts',
                'service_type_display': 'Договоры',
                'comment': 'Нужна помощь с договором аренды',
                'created_at': '2025-10-23T10:30:00Z'
            },
            response_only=True,
            status_codes=['201'],
        ),
    ]
)
class ConsultationRequestCreateView(generics.CreateAPIView):
    """
    Create consultation request and send WhatsApp notification asynchronously
    """
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer

    def create(self, request, *args, **kwargs):
        # Validate and save
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consultation = serializer.save()

        # Send WhatsApp in background thread (user doesn't wait!)
        def send_whatsapp():
            try:
                TelegramService.send_consultation_request_cloud_api(consultation)
            except Exception as e:
                logger.error(f"Failed to send WhatsApp for consultation {consultation.id}: {e}")

        thread = threading.Thread(target=send_whatsapp)
        thread.daemon = True
        thread.start()

        # Return immediately
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )


@extend_schema(
    tags=['Service Types'],
    summary='Get service types',
    description='Get all available service types for consultation',
    responses={
        200: OpenApiTypes.OBJECT,
    },
    examples=[
        OpenApiExample(
            'Service types response',
            value=[
                {'value': 'court_disputes', 'label': 'Суды и Споры'},
                {'value': 'business_registration', 'label': 'Регистрация бизнеса'},
                {'value': 'contracts', 'label': 'Договоры'},
                {'value': 'business_support', 'label': 'Сопровождение Бизнеса'},
                {'value': 'project_organization', 'label': 'Организация проектов и фестивалей'},
                {'value': 'personal_injury', 'label': 'Личная травма'},
            ],
            response_only=True,
        ),
    ]
)
class ServiceTypeListView(APIView):
    """
    Get available service types

    GET /api/service-types/
    """

    def get(self, request):
        service_types = [
            {
                'value': choice[0],
                'label': choice[1]
            }
            for choice in ServiceType.choices
        ]
        return Response(service_types)

@extend_schema(
    tags=['Consultation'],
    summary='List consultation requests',
    description='Get paginated list of all consultation requests',
    responses={
        200: ConsultationRequestSerializer(many=True),
    },
    examples=[
        OpenApiExample(
            'Consultation requests list',
            value=[
                {
                    'id': 1,
                    'name': 'Иван Иванов',
                    'email': 'ivan@example.com',
                    'phone': '+998901234567',
                    'service_type': 'contracts',
                    'service_type_display': 'Договоры',
                    'comment': 'Нужна помощь с договором аренды',
                    'created_at': '2025-10-23T10:30:00Z'
                },
                {
                    'id': 2,
                    'name': 'Петр Петров',
                    'email': 'petr@example.com',
                    'phone': '+998907654321',
                    'service_type': 'court_disputes',
                    'service_type_display': 'Суды и Споры',
                    'comment': 'Консультация по судебному спору',
                    'created_at': '2025-10-22T15:45:00Z'
                }
            ],
            response_only=True,
        ),
    ]
)
class ConsultationRequestListView(generics.ListAPIView):
    """
    Get list of all consultation requests
    
    GET /api/consultation/list/
    - Returns paginated list of consultation requests
    - Ordered by creation date (newest first)
    """
    queryset = ConsultationRequest.objects.all().order_by('-created_at')
    serializer_class = ConsultationRequestSerializer
