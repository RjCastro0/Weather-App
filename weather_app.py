import os
import pytz
from dotenv import load_dotenv
import requests
from datetime import *
from PIL import ImageTk
from geopy.geocoders import Nominatim
from geopy.geocoders import (
    GeocoderTimedOut,
    GeocoderServiceError,
    GeocoderUnavailable,
    GeocoderQueryError,
)
from timezonefinder import TimezoneFinder
from tkinter import messagebox, Tk, Label, Frame, PhotoImage, Button, Entry

# Create a window
root = Tk()
root.title("Weather App")
root.geometry("890x470+300+300")
root.resizable(False, False)
root.config(bg="#57adff")

load_dotenv()

API_KEY = os.getenv("API_KEY")
geolocator = Nominatim(user_agent=os.getenv("USER_AGENT"))
KELVIN_TO_CELSIUS = 273.15


# functions
def kelvin_to_celsius(temp: float) -> float:
    """
    Converts a temperature value from Kelvin to Celsius.

    Args:
        temp (float): The temperature value in Kelvin.

    Returns:
        float: The temperature value in Celsius.
    """
    return round(temp - KELVIN_TO_CELSIUS, 1)


def update_days_labels():
    """updates the labels of the days of the week"""
    days_labels = [day_one, day_two, day_three, day_four, day_five]
    for i in range(5):
        days_labels[i].config(text=(datetime.now() + timedelta(days=i)).strftime("%A"))


def get_timezone(loc):
    """gets the timezone of a location given its longitude and latitude"""
    timezone_finder = TimezoneFinder()
    return timezone_finder.timezone_at(lng=loc.longitude, lat=loc.latitude)


def get_weather_data_from_openweathermap(location):
    """Gets the current weather data from the OpenWeatherMap API.

    Args:
        location: A geopy Location object representing the latitude and longitude of the location.

    Returns:
        A dictionary containing the weather data, including temperature, humidity, pressure, wind speed, and description.
    """
    api = f"https://api.openweathermap.org/data/2.5/weather?lat={location.latitude}&lon={location.longitude}&appid={API_KEY}"
    try:
        response = requests.get(api, timeout=10)
        response.raise_for_status()
        json_data = response.json()
        return json_data
    except requests.exceptions.HTTPError as err:
        messagebox.showerror("Error", f"HTTP error: {err}")
    except requests.exceptions.Timeout as err:
        messagebox.showerror("Error", f"Timeout error: {err}")
    except requests.exceptions.RequestException as err:
        messagebox.showerror("Error", f"Request error: {err}")


def update_current_weather(json_data):
    """updates the current weather data

    Args:
        json_data: A dictionary containing the weather data, including temperature, humidity, pressure, wind speed, and description.

    Returns:None
    """

    temp = json_data["main"]["temp"]
    humidity = json_data["main"]["humidity"]
    pressure = json_data["main"]["pressure"]
    wind_speed = json_data["wind"]["speed"]
    description = json_data["weather"][0]["description"]

    temp_label.config(text=f"{kelvin_to_celsius(temp)}°C")
    humidity_label.config(text=f"{humidity}%")
    pressure_label.config(text=(pressure, "hPa"))
    wind_speed_label.config(text=(wind_speed, "m/s"))
    description_label.config(text=description)


def update_day_image(json_data):
    """updates the image of the current day

    Args:
        json_data: A dictionary containing the weather data,
        including temperature, humidity, pressure,
        wind speed, and description.

    Returns:None
    """
    day_image = json_data["weather"][0]["icon"]
    day_photo = ImageTk.PhotoImage(file=f"./Icons/{day_image}@2x.png")
    first_image.config(image=day_photo)
    first_image.image = day_photo


def get_weather():
    """gets the weather data from the OpenWeatherMap API"""
    city = text_field.get()
    try:
        location = geolocator.geocode(city)
    except GeocoderServiceError:
        messagebox.showerror("Error", "Geocoding service error")
        return
    except GeocoderTimedOut:
        messagebox.showerror("Error", "Geocoding service timed out")
        return
    except GeocoderUnavailable:
        messagebox.showerror("Error", "Geocoding service unavailable")
        return
    except GeocoderQueryError:
        messagebox.showerror("Error", "Geocoding service query error")
        return

    result = get_timezone(location)
    timezone.config(text=result)

    long_lat.config(
        text=f"Longitude: {round(location.longitude, 4)}°N, \nLatitude: {round(location.latitude, 4)}°E"
    )

    home = pytz.timezone(result)
    local_time = datetime.now(home)
    current_time = local_time.strftime("%I:%M %p")
    clock.config(text=current_time)

    json_data = get_weather_data_from_openweathermap(location)
    update_current_weather(json_data)
    update_day_image(json_data)

    update_days_labels()


# icon
image_icon = PhotoImage(file="Images/logo.png")
root.iconphoto(False, image_icon)

Round_box = PhotoImage(file="Images/Rounded Rectangle 1.png")
Label(root, image=Round_box, bg="#57adff").place(x=40, y=110)

# Labels
label1 = Label(root, text="Temperature", font=("Arial", 11), bg="#203243", fg="white")
label1.place(x=50, y=120)

label2 = Label(root, text="Humidity", font=("Arial", 11), bg="#203243", fg="white")
label2.place(x=50, y=140)

label3 = Label(root, text="Preassure", font=("Arial", 11), bg="#203243", fg="white")
label3.place(x=50, y=160)

label4 = Label(root, text="Wind Speed", font=("Arial", 11), bg="#203243", fg="white")
label4.place(x=50, y=180)

label5 = Label(root, text="Description", font=("Arial", 11), bg="#203243", fg="white")
label5.place(x=50, y=200)

# search bar
Search_image = PhotoImage(file="./Images/Rounded Rectangle 3.png")
myimage = Label(image=Search_image, bg="#57adff")
myimage.place(x=270, y=120)

weat_image = PhotoImage(file="./Images/Layer 7.png")
weather_image = Label(root, image=weat_image, bg="#203243")
weather_image.place(x=290, y=127)

text_field = Entry(
    root,
    justify="center",
    width=15,
    font=("poppins", 25, "bold"),
    bg="#203243",
    border=0,
    fg="white",
)
text_field.place(x=370, y=130)
text_field.focus()

Search_icon = PhotoImage(file="./Images/Layer 6.png")
myimage_icon = Button(
    image=Search_icon, borderwidth=0, cursor="hand2", bg="#203243", command=get_weather
)
myimage_icon.place(x=645, y=125)

# Bottom box
frame = Frame(root, width=900, bg="#212120", height=180)
frame.pack(side="bottom")

# bottom boxes
first_box = PhotoImage(file="./Images/Rounded Rectangle 2.png")
second_box = PhotoImage(file="./Images/Rounded Rectangle 2 copy.png")

Label(frame, image=first_box, bg="#212120").place(x=30, y=30)
Label(frame, image=second_box, bg="#212120").place(x=300, y=30)
Label(frame, image=second_box, bg="#212120").place(x=400, y=30)
Label(frame, image=second_box, bg="#212120").place(x=500, y=30)
Label(frame, image=second_box, bg="#212120").place(x=600, y=30)

# clock
clock = Label(root, font=("Helvetica", 30, "bold"), fg="white", bg="#57adff")
clock.place(x=30, y=20)


timezone = Label(root, font=("Helvetica", 20, "bold"), fg="white", bg="#57adff")
timezone.place(x=500, y=19)

long_lat = Label(root, font=("Helvetica", 10, "bold"), fg="white", bg="#57adff")
long_lat.place(x=700, y=50)


# showing weather values on screen
temp_label = Label(root, font=("Arial", 11), bg="#203243", fg="white")
temp_label.place(x=150, y=120)

humidity_label = Label(root, font=("Arial", 11), bg="#203243", fg="white")
humidity_label.place(x=150, y=140)

pressure_label = Label(root, font=("Arial", 11), bg="#203243", fg="white")
pressure_label.place(x=150, y=160)

wind_speed_label = Label(root, font=("Arial", 11), bg="#203243", fg="white")
wind_speed_label.place(x=150, y=180)

description_label = Label(root, font=("Arial", 11), bg="#203243", fg="white")
description_label.place(x=150, y=200)


# first cell
first_frame = Frame(root, width=230, height=132, bg="#282829")
first_frame.place(x=35, y=325)

day_one = Label(first_frame, font="arial 20", bg="#282829", fg="#fff")
day_one.place(x=100, y=5)

first_image = Label(first_frame, bg="#282829")
first_image.place(x=1, y=15)

day_temperature = Label(first_frame, bg="#282829", fg="#57adff", font="arial 15 bold")
day_temperature.place(x=100, y=50)


# second cell
second_frame = Frame(root, width=72, height=115, bg="#282829")
second_frame.place(x=304, y=325)

day_two = Label(second_frame, bg="#282829", fg="#fff")
day_two.place(x=10, y=5)

second_image = Label(second_frame, bg="#282829")
second_image.place(x=7, y=20)


# third cell
third_frame = Frame(root, width=72, height=115, bg="#282829")
third_frame.place(x=404, y=325)

day_three = Label(third_frame, bg="#282829", fg="#fff")
day_three.place(x=10, y=5)

third_image = Label(third_frame, bg="#282929")
third_image.place(x=7, y=20)


# fourth cell
fourth_frame = Frame(root, width=72, height=115, bg="#282829")
fourth_frame.place(x=504, y=325)

day_four = Label(fourth_frame, bg="#282829", fg="#fff")
day_four.place(x=10, y=5)

fourth_image = Label(fourth_frame, bg="#282929")
fourth_image.place(x=7, y=20)

# fifth cell
fifth_frame = Frame(root, width=72, height=115, bg="#282829")
fifth_frame.place(x=604, y=325)

day_five = Label(fifth_frame, bg="#282829", fg="#fff")
day_five.place(x=10, y=5)

fifth_image = Label(fifth_frame, bg="#282929")
fifth_image.place(x=7, y=20)


root.mainloop()
