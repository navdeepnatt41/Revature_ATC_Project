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
from sqlalchemy import create_engine, Engine, text

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
def top_10_busiest_routes(engine: Engine):
    query= text("""
        SELECT
            r.origin_airport_code,
            r.destination_airport_code,
            COUNT(*) AS flight_count
        FROM flight f
        JOIN route r ON f.route_id = r.route_id
        GROUP BY r.origin_airport_code, r.destination_airport_code
        ORDER BY flight_count DESC
        LIMIT 10
    """)
    
    top_10 = pd.read_sql_query(query, engine)
    top_10["route"] = (
        top_10["origin_airport_code"] + "->" + top_10["destination_airport_code"]
    )
    top_10 = top_10.sort_values("flight_count", ascending=True)
    
    plt.figure(figsize=(10, 6))
    plt.barh(top_10["route"], top_10["flight_count"])
    plt.title("Top 10 Busiest Routes by Flight Count")
    plt.xlabel("Flight Count")
    plt.ylabel("Route")
    plt.tight_layout()
    plt.show()

#  2. Histogram: distribution of departure times to identify peak hours

def departure_times_distribution(engine: Engine):
    query = text("SELECT departure_time FROM flight")
    df_departure_times = pd.read_sql_query(query, engine)

    df_departure_times['departure_time'] = pd.to_datetime(df_departure_times['departure_time'])

    hours = df_departure_times['departure_time'].dt.hour

    plt.figure(figsize=(10, 6))
    plt.hist(hours, bins=range(0, 25), edgecolor='black', color='skyblue', align='left')

    plt.xticks(range(0, 24))
    plt.xlabel('Hour of the Day (24-hour format)')
    plt.ylabel('Number of Flights')
    plt.title('Distribution of Flight Departures by Hour')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    plt.show()
    

#  3. Pie chart: flights by flight_status to montitor operational health

def flight_status_pie_chart(engine: Engine):
    query = text("SELECT flight_status FROM flight")
    df_flights = pd.read_sql_query(query, engine)
    status_counts = df_flights['flight_status'].value_counts()

    labels = status_counts.index
    sizes = status_counts.values

    colors = ['#66b3ff', '#99ff99', '#ffcc99', '#ff9999'] 

    # 4. Create the Pie Chart
    plt.figure(figsize=(10, 7))
    plt.pie(sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            startangle=140,
            colors=colors, 
            explode=[0.05] * len(labels),
            shadow=True)

    plt.title('Operational Health: Flights by Status')
    plt.axis('equal')
    plt.show()

#Bar Chart: for every aircraft, get the percentage of current_distance and maintance_interval to identify which aircraft are nearing their maintenance intervals
#   For each aircraft, show a heat map of how close it is to maintenance - color coded (green to red = perfect condition to needs maintenance now)
#    current distance = how many miles since last maintenance
#    current distance / interval = decimal of how close it is to needing maintenance
# 0.2 = maintenance not required right now, 0.9 = close to maintenance

#Line Chart: average delays by day(or week) to identify trends in delays over time
def delayed_flight_rate_trend(engine: Engine, by: str = "day"):
    if by not in ("day", "week"):
        raise ValueError("by must be 'day' or 'week'")

    period_expr = "DATE(departure_time)" if by == "day" else "DATE_TRUNC('week', departure_time)"

    query = text(f"""
        SELECT
            {period_expr} AS period,
            AVG(CASE WHEN flight_status = 'DELAYED' THEN 1.0 ELSE 0.0 END) * 100 AS delayed_rate_pct
        FROM flight
        GROUP BY 1
        ORDER BY 1
    """)

    df = pd.read_sql_query(query, engine)
    df["period"] = pd.to_datetime(df["period"])

    plt.figure(figsize=(10, 6))
    plt.plot(df["period"], df["delayed_rate_pct"], marker="o")
    plt.title(f"Delayed Flight Rate by {by.title()}")
    plt.xlabel(by.title())
    plt.ylabel("Delayed Flights (%)")
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.show()


#Scatter Plot: departure_time vs delay minutes (which we'll use diff colors for) to identify peak delay times throughout the day


