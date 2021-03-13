import json
import os
import sys

import requests as req
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

APIKEY = os.environ.get('API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_info = {}
    if request.method == 'POST':
        city = request.form['city_name']
        r = req.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={APIKEY}')
        j = json.loads(r.text)
        temp_c = j.get('main').get('temp')
        state = j.get('weather')[0].get('main')
        weather_info = {'city': city.upper(), 'state': state, 'degree': temp_c//100}

    return render_template('index.html', weather=weather_info)

# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
