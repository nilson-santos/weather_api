import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from asgiref.sync import sync_to_async
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.test import Client
from weather.models import UserRequest, WeatherData
from weather.tasks import collect_weather_data
import asyncio
import json
from utils import city_ids

# Configuração do client Django para testes
client = Client()

@pytest.mark.django_db
@pytest.mark.asyncio
class TestModels:
    async def test_weather_data_creation(self):
        # Função síncrona para criar UserRequest e WeatherData
        def create_user_request_and_weather_data():
            # Criar um UserRequest para associar com WeatherData
            user_request = UserRequest.objects.create(user_defined_id='test_user_id_for_weather_data')
            # Criar um WeatherData
            WeatherData.objects.create(
                user_request=user_request,
                city_id=123,
                temperature_celsius=25.0,
                humidity=60.0
            )
            return user_request

        # Executar a função síncrona dentro do contexto assíncrono
        user_request = await sync_to_async(create_user_request_and_weather_data)()

        # Função síncrona para consultar WeatherData
        def get_weather_data_entries():
            return WeatherData.objects.filter(user_request=user_request)

        # Consultar WeatherData
        weather_data_entries = await sync_to_async(get_weather_data_entries)()
        assert weather_data_entries.count() == 1
        entry = weather_data_entries.first()
        assert entry.temperature_celsius == 25.0
        assert entry.humidity == 60.0


@pytest.mark.django_db
@pytest.mark.asyncio
class TestViews:

    @patch('weather.views.collect_weather_data.delay', new_callable=AsyncMock)
    async def test_collect_weather_data_view(self, mock_collect_weather_data):
        response = await client.post(reverse('collect_weather_data'), {'user_defined_id': 'test_user_id'})
        assert response.status_code == 202
        assert json.loads(response.content) == {'message': 'Tarefa de coleta de dados iniciada'}
        mock_collect_weather_data.assert_called_once_with('test_user_id')

    @patch('weather.views.UserRequest.objects.get', return_value=MagicMock(user_defined_id='test_user_id'))
    @patch('weather.views.WeatherData.objects.filter', return_value=MagicMock(count=lambda: len(city_ids)))
    async def test_get_progress_view(self, mock_filter, mock_get):
        response = await client.get(reverse('get_progress', args=['test_user_id']))
        assert response.status_code == 200
        progress = (len(city_ids) / len(city_ids)) * 100
        assert json.loads(response.content) == {'progress': round(progress, 2)}

    @patch('weather.views.UserRequest.objects.get', side_effect=ObjectDoesNotExist)
    async def test_get_progress_view_user_not_found(self, mock_get):
        response = await client.get(reverse('get_progress', args=['nonexistent_user_id']))
        assert response.status_code == 404
        assert json.loads(response.content) == {'error': 'ID não encontrado'}

@pytest.mark.django_db
@pytest.mark.asyncio
class TestTasks:

    @patch('weather.tasks.aiohttp.ClientSession', new_callable=AsyncMock)
    @patch('weather.tasks.sync_to_async', new_callable=MagicMock)
    async def test_collect_weather_data(self, mock_sync_to_async, mock_client_session):
        mock_session_instance = AsyncMock()
        mock_client_session.return_value = mock_session_instance

        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            'main': {'temp': 25.0, 'humidity': 60.0}
        })
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response

        mock_user_request = MagicMock()
        mock_sync_to_async.return_value = mock_user_request

        await collect_weather_data('test_user_id')

        try:
            await sync_to_async(UserRequest.objects.get)(user_defined_id='test_user_id')
        except ObjectDoesNotExist:
            pytest.fail("UserRequest não foi criado")

        assert mock_session_instance.get.call_count == len(city_ids)
        weather_data_entries = await sync_to_async(WeatherData.objects.filter)(user_request=mock_user_request)
        assert weather_data_entries.count() == len(city_ids)
        for entry in weather_data_entries:
            assert entry.temperature_celsius == 25.0
            assert entry.humidity == 60.0

    @patch('weather.tasks.aiohttp.ClientSession', new_callable=AsyncMock)
    @patch('weather.tasks.sync_to_async', new_callable=MagicMock)
    async def test_rate_limit(self, mock_sync_to_async, mock_client_session):
        mock_session_instance = AsyncMock()
        mock_client_session.return_value = mock_session_instance

        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            'main': {'temp': 25.0, 'humidity': 60.0}
        })
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response

        mock_user_request = MagicMock()
        mock_sync_to_async.return_value = mock_user_request

        start_time = asyncio.get_event_loop().time()

        await collect_weather_data('rate_limit_test_user_id')

        elapsed_time = asyncio.get_event_loop().time() - start_time
        assert elapsed_time >= (len(city_ids) / 60.0)

    @patch('weather.tasks.aiohttp.ClientSession', new_callable=AsyncMock)
    @patch('weather.tasks.sync_to_async', new_callable=MagicMock)
    async def test_user_request_integrity(self, mock_sync_to_async, mock_client_session):
        mock_session_instance = AsyncMock()
        mock_client_session.return_value = mock_session_instance

        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            'main': {'temp': 25.0, 'humidity': 60.0}
        })
        mock_session_instance.get.return_value.__aenter__.return_value = mock_response

        mock_sync_to_async.side_effect = [MagicMock(), IntegrityError("Unique constraint failed")]

        with pytest.raises(IntegrityError):
            await collect_weather_data('duplicate_user_id')

        weather_data_entries = await sync_to_async(WeatherData.objects.filter)(user_request__user_defined_id='duplicate_user_id')
        assert weather_data_entries.count() == 0
