import serial
import time
import sys
import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

def GPS_Info():                                 #TODO: Move to a different class
    global NMEA_buff
    global GPVTG_arr
    global lat_in_degrees
    global long_in_degrees
    nmea_latitude = []
    nmea_longitude = []
    nmea_latitude = NMEA_buff[1]                #extract latitude from GPGGA string
    nmea_longitude = NMEA_buff[3]               #extract longitude from GPGGA string

    lat = float(nmea_latitude)                  #convert string into float for calculation
    longi = float(nmea_longitude)               #convertr string into float for calculation

    lat_in_degrees = convert_to_degrees(lat)    #get latitude in degree decimal format
    long_in_degrees = convert_to_degrees(longi) #get longitude in degree decimal format
    if NMEA_buff[4]=="W":
        long_in_degrees = "-" + long_in_degrees

#convert raw NMEA string into degree decimal format
def convert_to_degrees(raw_value):              #TODO: Move to a different class
    decimal_value = raw_value/100.00
    degrees = int(decimal_value)
    mm_mmmm = (decimal_value - int(decimal_value))/0.6
    position = degrees + mm_mmmm
    position = "%.4f" %(position)
    return position


gpgga_info = "$GPGGA,"
gpvtg_info = "$GPVTG,"
ser = serial.Serial ("/dev/ttyACM0",19200)              #Open port with baud rate
GPGGA_buffer = 0
NMEA_buff = 0
lat_in_degrees = 0
long_in_degrees = 0
current_speed = 0
max_speed = 0
speed_status = None
required_info = {}
led_colors = {
    "within_speed_limit": ["green", "green"],
    "nearing_speed_limit": ["orange", "orange"],
    "above_speed_limit": ["orange", "red"],
    "above_speed_limit_+5": ["red", "red"]
}

HERE_API_KEY = os.getenv('HERE_API_KEY')
HERE_API_URL = os.getenv('HERE_API_URL')
# print("HERE API KEY: ", HERE_API_KEY)

try:
    while True:
        speed_status = "within_speed_limit"                     # "green""green"-within speed limit, "orange""orange"-5mph within speed limit, "orange""red"-above speed limit less than 10, "red""red" - above speed limit more than 10
        received_data = (str)(ser.readline())                   #read NMEA string received
        GPGGA_data_available = received_data.find(gpgga_info)   #check for NMEA GPGGA string
        GPVTG_data_available = received_data.find(gpvtg_info)   #check for NMEA GPVYG string
        if (GPGGA_data_available>0):
            GPGGA_buffer = received_data.split("$GPGGA,",1)[1]  #store data coming after "$GPGGA," string
            NMEA_buff = (GPGGA_buffer.split(','))               #store comma separated data in buffer
            GPS_Info()                                          #get time, latitude, longitude
            # print("lat in degrees:", lat_in_degrees," long in degree: ", long_in_degrees, '\n')
            required_info["lat_in_degrees"] = lat_in_degrees    # TODO: add exception for lat and long
            required_info["long_in_degrees"] = long_in_degrees
        elif (GPVTG_data_available>0):
            GPVTG_buffer = received_data.split("$GPVTG,",1)[1]
            GPVTG_arr = (GPVTG_buffer.split(','))
            try:
               current_speed = int(float(GPVTG_arr[6])*0.62137119223733) #convert to mph
            except:
               current_speed = 0
            # print("Current speed: ", current_speed, "mph")
            required_info["current_speed"] = current_speed

        if len(required_info) == 3:
            url = HERE_API_URL.format(required_info['lat_in_degrees'], required_info['long_in_degrees'], required_info['lat_in_degrees'], required_info['long_in_degrees'], HERE_API_KEY)
            payload={}
            headers = {}
            response = requests.request("GET", url, headers=headers, data=payload)
            response_json = response.json()
            # print(response_json)
            if "maxSpeed" in (response_json["routes"][0]["sections"][0]["spans"][0]):
                max_speed = (response_json["routes"][0]["sections"][0]["spans"][0]["maxSpeed"])*2.23 #convert to mph by multiplying by 2.23
                max_speed = int(5 * round(max_speed/5)) #round to base of 5
                # print("Speed Limit: ", max_speed, "mph")
                if current_speed < max_speed-5:
                    speed_status = "within_speed_limit"
                if current_speed > max_speed-5 and current_speed <= max_speed:
                    speed_status = "nearing_speed_limit"
                if current_speed > max_speed and current_speed <= max_speed+5:
                    speed_status = "above_speed_limit"
                if current_speed > max_speed+5:
                    speed_status = "above_speed_limit_+5"
                # print(led_colors)
            telemetry = {
                "current_speed": str(current_speed)+"mph",
                "speed_limit": str(max_speed)+"mph",
                "speed_status": speed_status,
                "led_colors": led_colors[speed_status]
            }
            print(telemetry)
            with open("speed_limit_data.txt", 'a') as f:
                f.write(json.dumps(telemetry))
            required_info = {}
            time.sleep(1)

except KeyboardInterrupt:
    sys.exit(0)