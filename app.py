# import Dependices
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, distinct, desc

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Mmt = Base.classes.measurement
Sta = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"Welcome to my 'Home' page!<br/>"
        f"<table border=1>"
        f"<tr><th colspan=2>Available Routes</th></tr>"
        f"<tr><td>/api/v1.0/precipitation</td><td>View all precipitation information</td></tr>"
        f"<tr><td>/api/v1.0/stations</td><td>View a list of the all stations</td></tr>"
        f"<tr><td>/api/v1.0/tobs</td><td>View the last year of temperature observations for the last year of data</td></tr>"
        f"<tr><td>/api/v1.0/&lt;start&gt;</td><td>View the temperature [minimum, average, maximum] from the start date to the end of the data. Date format: yyyy-mm-dd</td></tr>"
        f"<tr><td>/api/v1.0/&lt;start&gt;/&lt;end&gt;</td><td>View the temperature [minimum, average, maximum] from the start date to the end date. Date format: yyyy-mm-dd</td></tr>"
        f"</table>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    print("Server received request for 'Precipitation' page ...")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    precip = session.query(Mmt.date, Mmt.prcp)
    session.close()

    precip_dict = {}
    for row in precip:
        precip_dict[row[0]]=row[1]
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page ...")
    session = Session(engine)
    stations = session.query(Sta.name)
    session.close()

    station_list = []
    for row in stations:
        station_list.append(row[0])
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def last_year():
    print("Server received request for 'Tobs' page ...")
    session = Session(engine)
    sta_counts = session.query(Mmt.station.distinct(),
                            func.count(Mmt.station).label('total')).\
                            group_by(Mmt.station).order_by(desc('total'))
    
    double_filt = session.query(Mmt.date, Mmt.station, Mmt.tobs).\
                filter(Mmt.station==sta_counts.first()[0]).\
                filter(Mmt.date >= '2016-08-23').\
                order_by(Mmt.date).all()
    session.close()

    double_filt_df = pd.DataFrame(double_filt, columns=['Date','Station','tobs'])
    observations = double_filt_df['tobs'].tolist()
    return jsonify(observations)

@app.route("/api/v1.0/<start>")
def temp_stats(start):
    print("Server received request for 'start range' page ...")
    session = Session(engine)
    temp_max = session.query(func.max(Mmt.tobs)).filter(Mmt.date >= start)
    temp_min = session.query(func.min(Mmt.tobs)).filter(Mmt.date >= start)
    temp_avg = session.query(func.avg(Mmt.tobs)).filter(Mmt.date >= start)
    session.close()

    temp_list = [temp_min[0][0], round(temp_avg[0][0],2), temp_max[0][0]]
    return jsonify(temp_list)

@app.route("/api/v1.0/<start>/<end>")
def temp_stats_range(start, end):
    print("Server received request for 'start-end range' page ...")
    session = Session(engine)
    temp_max = session.query(func.max(Mmt.tobs)).filter(Mmt.date >= start).filter(Mmt.date <= end)
    temp_min = session.query(func.min(Mmt.tobs)).filter(Mmt.date >= start).filter(Mmt.date <= end)
    temp_avg = session.query(func.avg(Mmt.tobs)).filter(Mmt.date >= start).filter(Mmt.date <= end)
    session.close()

    temp_list = [temp_min[0][0], round(temp_avg[0][0],2), temp_max[0][0]]
    return jsonify(temp_list)

if __name__ == '__main__':
    app.run(debug=True)