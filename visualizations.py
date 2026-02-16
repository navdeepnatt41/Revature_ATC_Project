"""
Global Route Network GraphSince you have latitude and longitude for airports and a route table connecting them, 
you can visualize the "hub and spoke" model of your airline.Logic: Use the route table to create a list of edges
(Origin $\rightarrow$ Destination) and the airport table for the node coordinates.
Visualization: A scatter plot of airport coordinates with lines (routes) connecting them. 
You can weight the thickness of the lines based on how many flights are scheduled on that route.

Matplotlib Tip: Use plt.annotate() to label the airport codes (JFK, LAX) next to the scatter points.


4. Fleet Distribution by Status (Donut Chart)
A clean way to see the "Ready-to-Fly" capacity of the airline.

Logic: Group the aircraft table by aircraft_status (AVAILABLE, DEPLOYED, AOG).

Visualization: A Donut chart (a pie chart with a white circle in the center). This is highly effective for dashboards.

Pandas Tip: df['aircraft_status'].value_counts().plot(kind='pie', wedgeprops=dict(width=0.5))
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, Engine

# I'm testing out how custom queries can be used with Pandas Dataframes:
def test_queries_with_pandas(engine: Engine):
    query = """
    SELECT 
        f.flight_id, 
        r.origin_airport_code, 
        r.destination_airport_code, 
        a.aircraft_model,
        f.departure_time
    FROM flight f
    JOIN route r ON f.route_id = r.route_id
    JOIN aircraft a ON f.aircraft_id = a.aircraft_id
    """

    df_flights = pd.read_sql_query(query, engine)

    print(df_flights.head(10))

if __name__ == "__main__":
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/merge_conflicts_flights_db"
    engine = create_engine(DATABASE_URL)
    print(test_queries_with_pandas(engine))
        
        
#   1. Bar Chart: top 10 most busiest routes by flight count
        #stretchgoal: localhost/visualizations/busiest_routes/?month=january
        #take user input for month and filter the data accordingly to show busiest routes for that month

#  2. Histogram: distribution of departure times to identify peak hours

#  3. Pie chart: flights by flight_status to montitor operational health

#Bar Chart: for every aircraft, get the percentage of current_distance and maintance_interval to identify which aircraft are nearing their maintenance intervals
#   For each aircraft, show a heat map of how close it is to maintenance - color coded (green to red = perfect condition to needs maintenance now)
#    current distance = how many miles since last maintenance
#   current distance / interval = decimal of how close it is to needing maintenance
# 0.2 = maintenance not required right now, 0.9 = close to maintenance

#Line Chart: average delays by day(or week) to identify trends in delays over time



#Scatter Plot: departure_time vs delay minutes (which we'll use diff colors for) to identify peak delay times throughout the day


