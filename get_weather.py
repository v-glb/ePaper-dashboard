# imports
import sys
sys.path.append(r'lib')
import signal
import epd2in7b
import epdconfig
import time
from PIL import Image,ImageDraw,ImageFont
import traceback
import time
import datetime
import pyowm
from config import owm_key

# REPLACE WITH YOUR OWM API KEY
owm = pyowm.OWM(owm_key)

# You can invoke the weather apis by City Name, City ID, Lat/Long or
# by Zip Code.
# According to Open Weather Map "We recommend to call API by city ID to get unambiguous result for your city."
# 
# Find your own city id here: 
# http://bulk.openweathermap.org/sample/city.list.json.gz
# Replace city_id below with the city id of your choice
#

# REPLACE WITH YOUR CITY ID
city_id = 2910831 # Hanover, DE, Germany

# An easy way to display icons and artwork on your ePaper display is to use a font like
# Meteocons, which maps font letters to specific icons, so by printing a character "B" you can print
# a Sunny icon!
#
# Open Weather Map has weather codes for the current weather report, that correspond to different
# conditions like sunny, cloudy, etc. Check Weather Condition Codes under 
# https://openweathermap.org/weather-conditions
# for the full list of weather codes. 
#
# Map weather code from OWM to meteocon icons.
#
# This enables us to easily use artwork and icons
# for display by simply using the character corresponding to that icon!
#
# Refer to http://www.alessioatzeni.com/meteocons/ for the mapping of meteocons to characters,
# and modify the dictionary below to change icons you want to use for different weather conditions!
# Meteocons is free to use - you can customize the icons - do consider contributing back to Meteocons!

weather_icon_dict = {200 : "6", 201 : "6", 202 : "6", 210 : "6", 211 : "6", 212 : "6", 
                     221 : "6", 230 : "6" , 231 : "6", 232 : "6", 

                     300 : "7", 301 : "7", 302 : "8", 310 : "7", 311 : "8", 312 : "8",
                     313 : "8", 314 : "8", 321 : "8", 
 
                     500 : "7", 501 : "7", 502 : "8", 503 : "8", 504 : "8", 511 : "8", 
                     520 : "7", 521 : "7", 522 : "8", 531 : "8",

                     600 : "V", 601 : "V", 602 : "W", 611 : "X", 612 : "X", 613 : "X",
                     615 : "V", 616 : "V", 620 : "V", 621 : "W", 622 : "W", 

                     701 : "M", 711 : "M", 721 : "M", 731 : "M", 741 : "M", 751 : "M",
                     761 : "M", 762 : "M", 771 : "M", 781 : "M", 

                     800 : "1", 

                     801 : "H", 802 : "N", 803 : "N", 804 : "Y"
}


def show_weather(epd):
    # Get Weather data from OWM
    obs = owm.weather_at_id(city_id)
    location = obs.get_location().get_name()
    weather = obs.get_weather()
    reftime = weather.get_reference_time()
    description = weather.get_detailed_status()
    temperature = weather.get_temperature(unit='celsius')
    humidity = weather.get_humidity()
    pressure = weather.get_pressure()
    clouds = weather.get_clouds()
    wind = weather.get_wind()
    rain = weather.get_rain()
    sunrise = weather.get_sunrise_time()
    sunset = weather.get_sunset_time()

    # Debug
    # print("location: " + location)
    # print("weather: " + str(weather))
    # print("description: " + description)
    # print("temperature: " + str(temperature))
    # print("humidity: " + str(humidity))
    # print("pressure: " + str(pressure))
    # print("clouds: " + str(clouds))
    # print("wind: " + str(wind))
    # print("rain: " + str(rain))
    # print("sunrise: " + time.strftime( '%H:%M', time.localtime(sunrise)))
    # print("sunset: " + time.strftime( '%H:%M', time.localtime(sunset)))

    try:
        # Drawing on the Horizontal image
        HBlackimage = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)  # 298*126
        HRedimage = Image.new('1', (epd2in7b.EPD_HEIGHT, epd2in7b.EPD_WIDTH), 255)  # 298*126     

        drawblack = ImageDraw.Draw(HBlackimage)
        drawred = ImageDraw.Draw(HRedimage)
        font24 = ImageFont.truetype('fonts/arial.ttf', 24)
        font16 = ImageFont.truetype('fonts/arial.ttf', 16)
        font20 = ImageFont.truetype('fonts/arial.ttf', 20)
        fontweather = ImageFont.truetype('fonts/meteocons-webfont.ttf', 30)
        fontweatherbig = ImageFont.truetype('fonts/meteocons-webfont.ttf', 60)  
        w1, h1 = font24.getsize(location)
        w2, h2 = font20.getsize(description) 
        w3, h3 = fontweatherbig.getsize(weather_icon_dict[weather.get_weather_code()])

        drawblack.text((10, 0), location, font = font24, fill = 0)
        drawblack.text((10 + (w1/2 - w2/2), 25), "     " + description, font = font20, fill = 0)    
        drawred.text((264 - w3 - 10, 0), weather_icon_dict[weather.get_weather_code()], font = fontweatherbig, fill = 0)
        drawblack.text((10, 45), "Observed at: " + time.strftime( '%I:%M %p', time.localtime(reftime)), font = font16, fill = 0)  
        tempstr = str("{0}{1}C".format(int(round(temperature['temp'])), u'\u00b0'))

        w4, h4 = font24.getsize(tempstr)
        drawblack.text((10, 70), tempstr, font = font24, fill = 0)
        drawred.text((10+w4, 70), "'", font = fontweather, fill = 0) 
        drawblack.text((150, 70), str("{0}{1} | {2}{3}".format(int(round(temperature['temp_min'])), u'\u00b0', int(round(temperature['temp_max'])), u'\u00b0')), font = font24, fill = 0) 
        drawblack.text((10, 100), str("{} hPA".format(int(round(pressure['press'])))), font = font20, fill = 0)
        drawblack.text((150, 100), str("{}% RH".format(int(round(humidity)))), font = font20, fill = 0) 
        drawred.text((20, 120), "A", font = fontweather, fill = 0)
        drawred.text((160, 120), "J", font = fontweather, fill = 0)
        drawblack.text((10, 150), time.strftime( '%I:%M %p', time.localtime(sunrise)), font = font20, fill = 0)
        drawblack.text((150, 150), time.strftime( '%I:%M %p', time.localtime(sunset)), font = font20, fill = 0) 

        epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRedimage))

        time.sleep(2)
        epd.sleep()

    except IOError as e:
       print ('traceback.format_exc():\n%s',traceback.format_exc())
       epdconfig.module_init()
       epdconfig.module_exit()
       exit()
