import streamlit as st
import requests
import pandas as pd
from datetime import datetime




st.set_page_config(
    page_title="Real-Time Weather App",
    page_icon="🌦️",
    layout="wide"
)




st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.weather-title {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 5px;
}

.weather-subtitle {
    text-align: center;
    font-size: 18px;
    margin-bottom: 30px;
}

.weather-card {
    padding: 20px;
    border-radius: 15px;
    border: 1px solid rgba(128,128,128,0.3);
    text-align: center;
    margin-bottom: 20px;
}

.metric-card {
    padding: 18px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.3);
    text-align: center;
}

.footer {
    text-align: center;
    margin-top: 40px;
    font-size: 14px;
}

</style>
""", unsafe_allow_html=True)




st.markdown(
    '<div class="weather-title">🌦️ Real-Time Weather App</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="weather-subtitle">'
    'Get current weather conditions and a 5-day forecast'
    '</div>',
    unsafe_allow_html=True
)




col1, col2 = st.columns([3, 1])

with col1:
    city = st.text_input(
        "🔍 Enter City Name",
        placeholder="Example: Bengaluru",
        help="Enter the name of a city to get weather information."
    )

with col2:
    unit = st.selectbox(
        "🌡️ Temperature Unit",
        ["Celsius", "Fahrenheit"]
    )




if unit == "Celsius":
    units = "metric"
    symbol = "°C"
else:
    units = "imperial"
    symbol = "°F"




search = st.button(
    "🔎 Get Weather",
    use_container_width=True
)




@st.cache_data(ttl=600)
def get_weather(city_name, api_key, units_value):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city_name,
        "appid": api_key,
        "units": units_value
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None




@st.cache_data(ttl=600)
def get_forecast(city_name, api_key, units_value):

    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city_name,
        "appid": api_key,
        "units": units_value
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    if response.status_code == 200:
        return response.json()

    return None




if search:

    if not city.strip():

        st.warning("⚠️ Please enter a city name.")

    else:

        try:

            
            API_KEY = st.secrets["OPENWEATHER_API_KEY"]

            

            with st.spinner("🌤️ Fetching weather information..."):

                data = get_weather(
                    city.strip(),
                    API_KEY,
                    units
                )

            

            if data is None:

                st.error(
                    "❌ City not found or weather service is unavailable."
                )

                st.info(
                    "Please check the city name and try again."
                )

                st.stop()

            

            temperature = data["main"]["temp"]

            feels_like = data["main"]["feels_like"]

            humidity = data["main"]["humidity"]

            description = data["weather"][0]["description"]

            wind_speed = data["wind"]["speed"]

            icon = data["weather"][0]["icon"]

            icon_url = (
                f"https://openweathermap.org/img/wn/"
                f"{icon}@2x.png"
            )

            sunrise_time = datetime.fromtimestamp(
                data["sys"]["sunrise"]
            )

            sunset_time = datetime.fromtimestamp(
                data["sys"]["sunset"]
            )

            

            st.divider()

            st.subheader(
                f"🌍 Weather in {data['name']}, "
                f"{data['sys'].get('country', '')}"
            )

          
            weather_col1, weather_col2 = st.columns(
                [1, 2]
            )

            with weather_col1:

                st.image(
                    icon_url,
                    width=130
                )

                st.markdown(
                    f"<h1 style='text-align:center;'>"
                    f"{temperature:.1f}{symbol}"
                    f"</h1>",
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"<p style='text-align:center;'>"
                    f"{description.title()}"
                    f"</p>",
                    unsafe_allow_html=True
                )

            with weather_col2:

                metric1, metric2 = st.columns(2)

                with metric1:

                    st.metric(
                        "🌡️ Feels Like",
                        f"{feels_like:.1f}{symbol}"
                    )

                    st.metric(
                        "💧 Humidity",
                        f"{humidity}%"
                    )

                with metric2:

                    st.metric(
                        "💨 Wind Speed",
                        f"{wind_speed}"
                    )

                    st.metric(
                        "🌅 Sunrise",
                        sunrise_time.strftime("%I:%M %p")
                    )

                st.metric(
                    "🌇 Sunset",
                    sunset_time.strftime("%I:%M %p")
                )

           

            st.divider()

            st.subheader("📅 5-Day Weather Forecast")

            with st.spinner("📊 Loading forecast..."):

                forecast_data = get_forecast(
                    city.strip(),
                    API_KEY,
                    units
                )

           

            if forecast_data is None:

                st.error(
                    "❌ Unable to load forecast information."
                )

                st.stop()

            

            forecast_list = []

            for item in forecast_data["list"]:

                forecast_icon = item["weather"][0]["icon"]

                forecast_icon_url = (
                    f"https://openweathermap.org/img/wn/"
                    f"{forecast_icon}@2x.png"
                )

                forecast_list.append(
                    {
                        "Date": item["dt_txt"],
                        "Temperature": item["main"]["temp"],
                        "Humidity": item["main"]["humidity"],
                        "Weather": item["weather"][0]["description"],
                        "Icon": forecast_icon_url
                    }
                )

            forecast_df = pd.DataFrame(
                forecast_list
            )

            

            st.dataframe(
                forecast_df,
                column_config={
                    "Date": st.column_config.DatetimeColumn(
                        "Date & Time",
                        format="DD MMM, HH:mm"
                    ),

                    "Temperature": st.column_config.NumberColumn(
                        "Temperature",
                        format=f"%.1f {symbol}"
                    ),

                    "Humidity": st.column_config.NumberColumn(
                        "Humidity",
                        format="%d %%"
                    ),

                    "Weather": st.column_config.TextColumn(
                        "Weather"
                    ),

                    "Icon": st.column_config.ImageColumn(
                        "Weather Icon",
                        width="small"
                    )
                },

                hide_index=True,

                use_container_width=True
            )

           

            forecast_df["Date"] = pd.to_datetime(
                forecast_df["Date"]
            )

           

            daily_forecast = (
                forecast_df
                .set_index("Date")["Temperature"]
                .resample("D")
                .mean()
                .reset_index()
            )

          

            st.subheader(
                "🌡️ 5-Day Temperature Forecast"
            )

            st.line_chart(
                daily_forecast.set_index("Date"),
                use_container_width=True
            )

           

            st.subheader(
                "📈 Daily Temperature Summary"
            )

            summary_df = daily_forecast.copy()

            summary_df["Date"] = summary_df[
                "Date"
            ].dt.strftime("%A, %d %b")

            summary_df["Temperature"] = (
                summary_df["Temperature"]
                .round(1)
            )

            summary_df.columns = [
                "Day",
                f"Average Temperature ({symbol})"
            ]

            st.dataframe(
                summary_df,
                hide_index=True,
                use_container_width=True
            )

      
      

        except KeyError:

            st.error(
                "❌ OpenWeather API key was not found."
            )

            st.info(
                "Please check your .streamlit/secrets.toml file."
            )

        except requests.exceptions.Timeout:

            st.error(
                "⏱️ Request timed out. "
                "Please check your internet connection and try again."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "🌐 Unable to connect to the weather service."
            )

        except requests.exceptions.RequestException:

            st.error(
                "❌ A network error occurred. "
                "Please try again."
            )

        except Exception as e:

            st.error(
                "❌ Something went wrong."
            )

            st.write(
                f"Technical details: {e}"
            )


