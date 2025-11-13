from django.urls import path
from . import views

urlpatterns = [
    path('api/consultation/', views.ConsultationRequestCreateView.as_view(), name='create_consultation'),
    path('api/consultation/list/', views.ConsultationRequestListView.as_view(), name='list_consultations'),
    path('api/service-types/', views.ServiceTypeListView.as_view(), name='service_types'),
]