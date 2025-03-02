# -*- coding: utf-8 -*-
"""
Created on Tue Feb 25 23:42:10 2025

@author: rwsmy
"""

#from ..rocketpy import Environment, SolidMotor, Rocket, Flight
import datetime
from rocketpy.motors import SolidMotor
from rocketpy.rocket import Rocket
from rocketpy.environment import Environment
from rocketpy.simulation import Flight
import json

env = Environment(latitude=21.339260, longitude=-157.960922, elevation=50)

tomorrow = datetime.date.today() + datetime.timedelta(days=1)

env.set_date(
    (tomorrow.year, tomorrow.month, tomorrow.day, 12)) #Hour given in UTC time

env.set_atmospheric_model(type="Forecast", file="GFS")
env.max_expected_height = 5000 # adjust the plots to this height
#env.info()

with open("parameters.json", mode="r", encoding="utf-8") as read_file:
    bashful = json.load(read_file)

brock = Rocket(**bashful['rocket'])
bmotor = SolidMotor(**{k: v for k, v in bashful['motors'].items() if k != "position"})
brock.add_motor(bmotor,bashful['motors']['position'])
brock.add_nose(**bashful['nosecones'])
brock.add_trapezoidal_fins(**bashful['trapezoidal_fins']['0'])
#brock.add_trapezoidal_fins(**bashful['trapezoidal_fins']['1'])
brock.add_parachute(**bashful['parachutes']['0'])

#brock.plots.static_margin()
#brock.draw()

test_flight = Flight(
    rocket=brock, environment=env, rail_length=5.2, inclination=85, heading=0
    )
test_flight.info()
test_flight.all_info()