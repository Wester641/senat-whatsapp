from rest_framework import serializers

from legal_form.models import ConsultationRequest


class ConsultationRequestSerializer(serializers.ModelSerializer):
    service_type_display = serializers.CharField(
        source='get_service_type_display',
        read_only=True
    )

    class Meta:
        model = ConsultationRequest
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'service_type',
            'service_type_display',
            'comment',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_phone(self, value):
        # Basic phone validation
        if not value.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise serializers.ValidationError("Неверный формат телефона")
        return value