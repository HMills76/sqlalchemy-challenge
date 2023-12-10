# Import the dependencies.
from flask import Flask, jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurements = Base.classes.measurement
Stations = Base.classes.station

# Create our session (link) from Python to the DB
#session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    session = Session(engine)    

    first_station = session.query(Measurements.station, func.count(Measurements.date)).\
            group_by(Measurements.station).\
            order_by(func.count(Measurements.date).desc()).first()

    last_date = dt.datetime(2017,8,23) - dt.timedelta(weeks=52)

    last_months = session.query(Measurements.date,Measurements.prcp).\
            filter(Measurements.station == first_station[0]).filter(Measurements.date >= last_date).all()
    
    session.close()
    
    first_station_precip = []
    for date, prcp in last_months:
        final_precip_dict = {}
        final_precip_dict["date"] = date
        final_precip_dict["prcp"] = prcp
        first_station_precip.append(final_precip_dict)

    return jsonify(first_station_precip)

@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    results = session.query(Stations.station).all()

    session.close()
    
    station_list = list(np.ravel(results))

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    first_station = session.query(Measurements.station).\
            group_by(Measurements.station).\
            order_by(func.count(Measurements.date).desc()).first()

    most_recent_date = session.query(Measurements.date).order_by(Measurements.date.desc()).first().date

    last_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')  - dt.timedelta(days=365)
    
    last_months = session.query(Measurements.date,Measurements.tobs).\
                    filter(Measurements.station == first_station[0]).filter(Measurements.date >= last_date).all()
        
    session.close()
    
    first_station_temps = []
    for date, tobs in last_months:
        final_temps_dict = {}
        final_temps_dict["date"] = date
        final_temps_dict["tobs"] = tobs
        first_station_temps.append(final_temps_dict)

    return jsonify(first_station_temps)

@app.route("/api/v1.0/<start_date>/")
def start_only(start_date):

    session = Session(engine)

    results = session.query(func.min(Measurements.tobs),\
                     func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                     filter(Measurements.date >= start_date).all()
    session.close() 

    tobs = []

    for min, avg, max in results:
        final_tobs = {}
        final_tobs["min"] = min
        final_tobs["avg"] = avg
        final_tobs["max"] = max
        tobs.append(final_tobs)

    
    return jsonify(tobs)


@app.route("/api/v1.0/<start_date>/<end_date>/")
def start_end(start_date,end_date):

    session = Session(engine)

    results = session.query(func.min(Measurements.tobs),\
                     func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                     filter(Measurements.date >= start_date).\
                     filter(Measurements.date <= end_date).all()
    session.close() 

    tobs = {}

    tobs["min"] = results[0][0]
    tobs["avg"] = results[0][1]
    tobs["max"] = results[0][2]
    
    return jsonify(tobs)

if __name__ == '__main__':
    app.run(debug=True)