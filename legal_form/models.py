# models.py
from django.db import models


class ServiceType(models.TextChoices):
    COURT_DISPUTES = 'court_disputes', 'Суды и Споры'
    BUSINESS_REGISTRATION = 'business_registration', 'Регистрация бизнеса'
    CONTRACTS = 'contracts', 'Договоры'
    BUSINESS_SUPPORT = 'business_support', 'Сопровождение Бизнеса'
    PROJECT_ORGANIZATION = 'project_organization', 'Организация проектов и фестивалей'
    PERSONAL_INJURY = 'personal_injury', 'Личная травма'


class ConsultationRequest(models.Model):
    name = models.CharField(max_length=200, verbose_name='Имя')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    service_type = models.CharField(
        max_length=50,
        choices=ServiceType.choices,
        verbose_name='Тип услуги'
    )
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запрос на консультацию'
        verbose_name_plural = 'Запросы на консультацию'

    def __str__(self):
        return f"{self.name} - {self.service_type}"