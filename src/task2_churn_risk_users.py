from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

def initialize_spark(app_name="Task2_Churn_Risk_Users"):
    """
    Initialize and return a SparkSession.
    """
    spark = SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()
    return spark

def load_data(spark, file_path):
    """
    Load the movie ratings data from a CSV file into a Spark DataFrame.
    """
    schema = """
        UserID INT, MovieID INT, MovieTitle STRING, Genre STRING, Rating FLOAT, ReviewCount INT, 
        WatchedYear INT, UserLocation STRING, AgeGroup STRING, StreamingPlatform STRING, 
        WatchTime INT, IsBingeWatched BOOLEAN, SubscriptionStatus STRING
    """
    df = spark.read.csv(file_path, header=True, schema=schema)
    return df

def identify_churn_risk_users(df):
    """
    Identify users with canceled subscriptions and low watch time (<100 minutes).
    """
    # Filter for users with canceled subscriptions and low watch time
    churn_risk = df.filter((col("SubscriptionStatus") == "Canceled") & (col("WatchTime") < 100))
    
    # Count unique users that match these criteria
    churn_risk_count = churn_risk.select("UserID").distinct().count()
    
    # Get total unique users for reference
    total_users = df.select("UserID").distinct().count()
    
    # Create a DataFrame with the results
    schema = StructType([
        StructField("Churn Risk Users", StringType(), False),
        StructField("Total Users", IntegerType(), False)
    ])
    
    result_df = df.sparkSession.createDataFrame([
        ("Users with low watch time & canceled subscriptions", churn_risk_count)
    ], schema=schema)
    
    return result_df

def write_output(result_df, output_path):
    """
    Write the result DataFrame to a CSV file.
    """
    result_df.coalesce(1).write.csv(output_path, header=True, mode='overwrite')

def main():
    """
    Main function to execute Task 2.
    """
    spark = initialize_spark()

    input_file = "/workspaces/handson-7-spark-structured-api-movie-ratings-analysis-revanth181418/input/movie_ratings_data.csv"
    output_file = "/workspaces/handson-7-spark-structured-api-movie-ratings-analysis-revanth181418/Outputs/churn_risk_users.csv"

    df = load_data(spark, input_file)
    result_df = identify_churn_risk_users(df)  # Corrected here
    write_output(result_df, output_file)

    spark.stop()

if __name__ == "__main__":
    main()
