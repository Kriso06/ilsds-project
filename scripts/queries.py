QUERIES={
    "q1_monthly_trip_counts":"""
        SELECT
            strftime('%Y-%m', tpep_pickup_datetime) AS pickup_month,
            COUNT(*) AS trip_count
        FROM {table}
        GROUP BY pickup_month
        ORDER BY pickup_month;
    """,

    "q2_revenue_by_payment_type":"""
        SELECT
            payment_type,
            COUNT(*) AS trip_count,
            ROUND(SUM(total_amount),2) AS total_revenue,
            ROUND(AVG(total_amount),2) AS avg_revenue
        FROM {table}
        GROUP BY payment_type
        ORDER BY total_revenue DESC;
    """,

    "q3_avg_fare_tip_by_passenger_count":"""
        SELECT
            passenger_count,
            COUNT(*) AS trip_count,
            ROUND(AVG(fare_amount),2) AS avg_fare,
            ROUND(AVG(tip_amount),2) AS avg_tip
        FROM {table}
        GROUP BY passenger_count
        ORDER BY passenger_count;
    """,

    "q4_top_10_pickup_zones":"""
        SELECT 
            z.Zone AS pickup_zone,
            z.Borough AS pickup_borough,
            COUNT(*) AS trip_count
        FROM {table} t
        JOIN zones z
            ON t.PULocationID=z.LocationID
        GROUP BY z.Zone, z.Borough
        ORDER BY trip_count DESC
        LIMIT 10
    """,

    "q5_top_10_routes":"""
        SELECT 
            pu.Zone AS pickup_zone,
            dz.Zone AS dropoff_zone,
            COUNT(*) AS trip_count
        FROM {table} t
        JOIN zones pu
            ON t.PULocationID=pu.LocationID
        JOIN zones dz
            ON t.DOLocationID=dz.LocationID
        GROUP BY pu.Zone, dz.Zone
        ORDER BY trip_count DESC
        LIMIT 10;
    """,

    "q6_revenue_by_borough":"""
        SELECT 
            z.Borough,
            COUNT(*) AS trip_count,
            ROUND(SUM(t.total_amount),2) AS total_revenue
        FROM {table} t
        JOIN zones z
            ON t.PULocationID=z.LocationID
        GROUP BY z.Borough
        ORDER BY total_revenue DESC;
    """,

    "q7_zone_revenue_rank":"""
        SELECT 
            z.Zone,
            ROUND(SUM(t.total_amount),2) AS total_revenue,
            RANK() OVER (ORDER BY SUM(t.total_amount) DESC) AS revenue_rank
        FROM {table} t
        JOIN zones z
            ON t.PULocationID=z.LocationID
        GROUP BY z.Zone
        ORDER BY revenue_rank
        LIMIT 10;
    """,

    "q8_running_daily_revenue":"""
        SELECT
            pickup_date,
            daily_revenue,
            SUM(daily_revenue) OVER (ORDER BY pickup_date) AS running_revenue
        FROM(
            SELECT 
                date(tpep_pickup_datetime) AS pickup_date,
                SUM(total_amount) AS daily_revenue
            FROM {table}
            GROUP BY date(tpep_pickup_datetime)
        ) d
        ORDER BY pickup_date;
    """,

    "q9_join_heavy_payment_rate_borough":"""
        SELECT
            z.Borough,
            payment_type,
            RatecodeID,
            COUNT(*) AS trip_count,
            ROUND(AVG(total_amount),2) AS avg_total_amount,
            ROUND(AVG(total_amount),2) AS total_revenue
        FROM {table} t
        JOIN zones z
            ON t.PULocationID=z.LocationID
        GROUP BY z.Borough, payment_type, RatecodeID
        ORDER BY total_revenue DESC
        LIMIT 20;
    """,

    "q10_long_high_value_trips_by_hour":"""
        SELECT
            strftime('%H', tpep_pickup_datetime) AS pickup_hour,
            COUNT(*) AS trip_count,
            ROUND(AVG(trip_distance),2) AS avg_distance,
            ROUND(AVG(total_amount),2) AS avg_total_amount,
            ROUND(SUM(total_amount),2) AS total_revenue
        FROM {table}
        WHERE trip_distance>10 AND total_amount>50
        GROUP BY pickup_hour
        ORDER BY pickup_hour;
    """,
}