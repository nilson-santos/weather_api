# Django Weather API Test

This is a Django application designed to interact with the OpenWeatherMap API, storing weather data such as City ID, Temperature in Celsius, and Humidity in a local SQLite database. The application is containerized using Docker Compose for easy deployment.

## Features

- Collect weather data for multiple cities using the OpenWeatherMap API.
- Store and manage the data in an SQLite database.
- Two primary endpoints for interacting with the data:
  - **POST /api/weather/collect/**: Collect weather data for a specific `user_defined_id`.
  - **GET /api/weather/progress/{user_defined_id}**: Check the progress of data collection for a given `user_defined_id`.

## Endpoints

### 1. Collect Weather Data
- **URL**: `http://localhost:8000/api/weather/collect/`
- **Method**: POST
- **Parameters**: 
  - `user_defined_id`: The unique identifier for the data collection process.
- **Description**: Initiates the collection of weather data for the cities associated with the provided `user_defined_id`. This process fetches data from the OpenWeatherMap API and stores it in the database.

### 2. Check Collection Progress
- **URL**: `http://localhost:8000/api/weather/progress/{user_defined_id}`
- **Method**: GET
- **Parameters**:
  - `user_defined_id`: The unique identifier for which you want to check the data collection progress.
- **Description**: Retrieves the progress status of the data collection process for the specified `user_defined_id`.

## Setup and Installation

### Prerequisites

- Docker and Docker Compose installed on your system.
- An API key from [OpenWeatherMap](https://openweathermap.org/api) to fetch weather data.

### Clone the Repository

```bash
git clone https://github.com/yourusername/django-weather-api.git
cd django-weather-api
```

### Running the Application

1. Build and start the Docker containers:

```bash
docker-compose up -d
```

### Usage
You can use tools like **Insomnia** or **Postman** to interact with the API endpoints:

1. Collect Data: Send a POST request to http://localhost:8000/api/weather/collect/ with a JSON body containing the user_defined_id.
2. Check Progress: Send a GET request to http://localhost:8000/api/weather/progress/{user_defined_id} to check the progress of data collection.