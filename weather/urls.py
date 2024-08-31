from django.urls import path
from .views import collect_weather_data_view, get_progress


urlpatterns = [
    path('collect/', collect_weather_data_view, name='collect_weather_data'),  # Endpoint POST
    path('progress/<str:user_defined_id>/', get_progress, name='get_progress'),  # Endpoint GET
]


