import sys
from datetime import datetime, timezone

import requests as req
from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db?check_same_thread=False'
app.secret_key = 'asf043m2m5oddd000sdds8343430fffd01233kkkavvbt'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)

APIKEY = ''
WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name


db.create_all()
db.session.commit()


def get_daytime(time, response):
    """
    :param time: timestamp in unix seconds
    :param response: response from weather api
    :return: str day/evening-morning/night
    """
    if response['sys']['sunrise'] < time <= response['sys']['sunset'] - 3600:
        return 'day'
    elif response['sys']['sunrise'] - 3600 < time < response['sys']['sunrise'] + 3600 or \
            response['sys']['sunset'] - 3600 < time < response['sys']['sunset'] + 3600:
        return 'evening-morning'
    else:
        return 'night'


def call_weather_api(city, units='metric'):
    """
    :param city: city name
    :param units: metric/imperial
    :return: dict{city:response}
    """
    params = {'q': city, 'appid': APIKEY, 'units': units}
    r = req.get(WEATHER_ENDPOINT, params=params)
    if not r:
        return
    resp = r.json()
    if not r.raise_for_status():
        time_now = int(datetime.now(tz=timezone.utc).timestamp())
        time_of_day = get_daytime(time_now, resp)
        return {resp['name']: {'id': city.id,
                               'condition': resp['weather'][0]['main'],
                               'temp': str(resp['main']['temp']),
                               'time_now': time_now, 'time_of_day': time_of_day}}


@app.route('/', methods=['GET'])
def index():
    weather_info = {}

    for city in City.query.all():
        weather_info.update(call_weather_api(city))

    return render_template('index.html', weather=weather_info)


@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        city = City(name=request.form['city_name'])
        call_weather_api(city)
        if call_weather_api(city) is None:
            flash("The city doesn't exist!")
        elif bool(City.query.filter_by(name=str(city)).first()):
            flash('The city has already been added to the list!')
        else:
            db.session.add(city)
            db.session.commit()
    return redirect('/')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    city = City.query.filter_by(id=city_id).first()
    db.session.delete(city)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()
