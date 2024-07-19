import streamlit as st
import requests
import datetime
import pandas as pd
import plotly.express as px

# OpenWeather API key
API_KEY = "ae3a09bacee8313ac35ba004aa1cde60"

def get_weather_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    return response.json()

def get_forecast_data(city):
    base_url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    return response.json()

def predict_rain(description):
    rain_keywords = ['rain', 'drizzle', 'shower']
    return any(keyword in description.lower() for keyword in rain_keywords)

def main():
    st.title("Advanced Weather App")

    # User input for city
    city = st.text_input("Enter a city name:", "London")

    if st.button("Get Weather"):
        weather_data = get_weather_data(city)
        forecast_data = get_forecast_data(city)

        if weather_data["cod"] != "404":
            # Current weather
            temperature = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            description = weather_data["weather"][0]["description"]
            wind_speed = weather_data["wind"]["speed"]
            dt = datetime.datetime.fromtimestamp(weather_data["dt"])

            # Display current weather information
            st.subheader(f"Current Weather in {city}")
            st.write(f"Date and Time: {dt}")
            st.write(f"Temperature: {temperature}°C")
            st.write(f"Humidity: {humidity}%")
            st.write(f"Description: {description.capitalize()}")
            st.write(f"Wind Speed: {wind_speed} m/s")

            # Rain prediction
            rain_prediction = predict_rain(description)
            st.write(f"Rain Prediction: {'Likely' if rain_prediction else 'Unlikely'}")

            # 5-day forecast
            st.subheader("5-Day Forecast")
            forecast_list = forecast_data['list']
            
            # Prepare data for chart
            df = pd.DataFrame(forecast_list)
            df['dt'] = pd.to_datetime(df['dt'], unit='s')
            df['temp'] = df['main'].apply(lambda x: x['temp'])
            df['description'] = df['weather'].apply(lambda x: x[0]['description'])

            # Group by date and get daily averages
            daily_data = df.groupby(df['dt'].dt.date).agg({
                'temp': 'mean',
                'description': lambda x: x.value_counts().index[0]
            }).reset_index()

            # Display daily forecast
            for _, row in daily_data.iterrows():
                st.write(f"{row['dt']}: {row['temp']:.1f}°C, {row['description'].capitalize()}")

            # Create temperature trend chart
            fig = px.line(daily_data, x='dt', y='temp', title='5-Day Temperature Trend')
            fig.update_xaxes(title_text='Date')
            fig.update_yaxes(title_text='Temperature (°C)')
            st.plotly_chart(fig)

        else:
            st.error("City not found. Please check the spelling and try again.")

if __name__ == "__main__":
    main()