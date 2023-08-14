import requests
from datetime import datetime
import smtplib
import time
import os
import json

admin_info = os.getenv('ADMIN_JSON_INFO')
with open(admin_info, 'r') as file:
    contents = file.read()
    admin_json_info = json.loads(contents)

FROM_EMAIL = admin_json_info['personal_info']['dummy_email']
FROM_EMAIL_PASSWORD = admin_json_info['personal_info']['dummy_email_password']
TO_EMAIL = admin_json_info['personal_info']['my_email']

#your Current position
MY_CITY = 'Seoul'
geocoding_params = {
    'q': MY_CITY,
    'appid': admin_json_info['weather']['api_key']
}
response = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=geocoding_params)
geocoding_result = response.json()
MY_LAT = geocoding_result[0]['lat']  # Your latitude
MY_LONG = geocoding_result[0]['lon']  # Your longitude


def is_issoverhead():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    iss_data = response.json()

    # ISS current position
    iss_latitude = float(iss_data["iss_position"]["latitude"])
    iss_longitude = float(iss_data["iss_position"]["longitude"])

    if MY_LAT - 5 <= iss_latitude <= MY_LAT + 5 and MY_LONG - 5 < iss_longitude < MY_LONG + 5:
        return True

def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    my_data = response.json()
    sunrise = int(my_data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(my_data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now()
    current_hour = time_now.hour

    if current_hour >= sunset or current_hour <= sunrise:
        return True


#Your position is within +5 or -5 degrees of the ISS position.
while True:
    time.sleep(60)
    if is_issoverhead() and is_night():
        with smtplib.SMTP("smtp.gmail.com", port=587) as connect:
            connect.starttls()
            connect.login(user=FROM_EMAIL, password=FROM_EMAIL_PASSWORD)
            print("Log in was successful.")
            connect.sendmail(from_addr=FROM_EMAIL,
                             to_addrs=TO_EMAIL,
                             msg="Subject:Look Up!\n\nThe ISS is on your head! Go out and look up the sky!")
            print("Email has been sent.")





