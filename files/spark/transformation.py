from pyspark.sql import functions as f
from os.path import join
from pyspark.sql import SparkSession
import argparse

def get_tweets_data(df):
    tweet_df = df.select(f.explode("data").alias("tweets"))\
        .select("tweets.author_id", "tweets.conversation_id",
        "tweets.created_at", "tweets.id",
        "tweets.public_metrics.*", "tweets.text")
    return tweet_df

def get_users_data(df):
    users = df.select(f.explode("includes.users").alias("users")).select("users.*")
    return users

def export_delta(df, dest):
    df.write.format("delta").mode("overwrite").save(dest)

def twitter_transformation(spark, source, dest, process_date):
    df = spark.read.format("json").load(source)
    tweet_df = get_tweets_data(df).withColumn('process_date', f.to_date(f.lit(process_date)))
    users = get_users_data(df).withColumn('process_date', f.to_date(f.lit(process_date)))

    table_dest = join(dest,"{table_name}")

    export_delta(tweet_df, table_dest.format(table_name="tweets"))
    export_delta(users, table_dest.format(table_name="users"))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Spark Twitter Transformation")

    parser.add_argument("--source", required = True)
    parser.add_argument("--dest", required = True)
    parser.add_argument("--process_date", required = True)
    
    args = parser.parse_args()

    spark = SparkSession\
    .builder\
    .getOrCreate()

    twitter_transformation(spark, args.source, args.dest, args.process_date)


    #./bin/spark-submit /files/spark/transformation.py --source s3a://datalake/twitter_datascience --dest s3a://datalake --process_date 2023-09-07