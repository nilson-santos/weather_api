
from .models import WeatherData
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .tasks import collect_weather_data
from .models import UserRequest
from utils import city_ids

@csrf_exempt
@require_POST
def collect_weather_data_view(request):
    user_defined_id = request.POST.get('user_defined_id')
    if user_defined_id:
        collect_weather_data.delay(user_defined_id)  # Chama a tarefa Celery
        return JsonResponse({'message': 'Tarefa de coleta de dados iniciada'}, status=202)
    else:
        return JsonResponse({'error': 'ID do usuário não fornecido'}, status=400)


@require_http_methods(["GET"])
def get_progress(request, user_defined_id):
    try:
        user_request = UserRequest.objects.get(user_defined_id=user_defined_id)
        weather_data_count = WeatherData.objects.filter(user_request=user_request).count()
        total_cities = len(city_ids)  # Total de cidades configuradas
        progress = (weather_data_count / total_cities) * 100
        return JsonResponse({'progress': round(progress, 2)})
    except UserRequest.DoesNotExist:
        return JsonResponse({'error': 'ID não encontrado'}, status=404)
