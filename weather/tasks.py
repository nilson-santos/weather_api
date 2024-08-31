from asgiref.sync import sync_to_async
from celery import shared_task
import aiohttp
import asyncio
from .models import UserRequest, WeatherData
from utils import city_ids
from project.settings import OPEN_WEATHER_API_KEY, OPEN_WEATHER_API_URL


# Rate limiting
RATE_LIMIT = 60  # 60 requests per minute
RATE_LIMIT_PERIOD = 60  # in seconds

# Async function to fetch weather data
async def fetch_and_save_weather_data(session, city_id, user_request):
    url = f"{OPEN_WEATHER_API_URL}?id={city_id}&appid={OPEN_WEATHER_API_KEY}&units=metric"
    async with session.get(url) as response:
        response.raise_for_status()
        data = await response.json()

        # Save the weather data in sync context
        await sync_to_async(WeatherData.objects.create)(
            user_request=user_request,
            city_id=city_id,
            temperature_celsius=data['main']['temp'],
            humidity=data['main']['humidity']
        )

# Task to collect weather data
@shared_task
def collect_weather_data(user_defined_id):
    async def main():
        # Create UserRequest in sync context
        user_request = await sync_to_async(UserRequest.objects.create)(user_defined_id=user_defined_id)

        semaphore = asyncio.Semaphore(RATE_LIMIT)  # Semaphore to limit the number of concurrent requests

        async with aiohttp.ClientSession() as session:
            tasks = []
            for city_id in city_ids:
                async with semaphore:
                    task = asyncio.ensure_future(fetch_and_save_weather_data(session, city_id, user_request))
                    tasks.append(task)
                    await asyncio.sleep(RATE_LIMIT_PERIOD / RATE_LIMIT)  # Sleep to respect rate limit

            await asyncio.gather(*tasks)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    return {'success': 'Dados coletados com sucesso'}, 200
