from django.db import models

class UserRequest(models.Model):
    user_defined_id = models.CharField(max_length=255, unique=True)
    datetime_of_request = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_defined_id

class WeatherData(models.Model):
    user_request = models.ForeignKey(UserRequest, on_delete=models.CASCADE, related_name='weather_data')
    city_id = models.IntegerField()
    temperature_celsius = models.FloatField()
    humidity = models.FloatField()

    def __str__(self):
        return f"City {self.city_id} for {self.user_request.user_defined_id}"
