from django.contrib import admin
from .models import ConsultationRequest


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'service_type', 'created_at']
    list_filter = ['service_type', 'created_at']
    search_fields = ['name', 'email', 'phone', 'comment']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Контактная информация', {
            'fields': ('name', 'email', 'phone')
        }),
        ('Детали запроса', {
            'fields': ('service_type', 'comment')
        }),
        ('Системная информация', {
            'fields': ('created_at',)
        }),
    )