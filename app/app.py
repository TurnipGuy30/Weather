from os import environ, path

from dotenv import load_dotenv
import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ['DATABASE_URL']
APPID = environ['APPID']

db = SQLAlchemy(app)

def api_url(city) -> str:
	return f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={APPID}'

class City(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)

@app.before_first_request
def create_tables():
	db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index() -> str:
	if request.method == 'POST':
		if new_city := request.form.get('city'):
			new_city_obj = City(name=new_city)
			db.session.add(new_city_obj)
			db.session.commit()

	cities = City.query.all()
	weather_data = []

	for city in cities:
		r = requests.get(api_url(city.name)).json()
		weather = {
			'city': city.name,
			'temperature': round(r['main']['temp']),
			'description': r['weather'][0]['description'],
			'icon': r['weather'][0]['icon'],
		}
		weather_data.append(weather)

	return render_template('weather.html', weather_data=weather_data)

if __name__ == '__main__':
	app.run(debug=True)
