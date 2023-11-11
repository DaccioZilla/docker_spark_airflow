import pyspark.sql.functions as f
from pyspark.sql import SparkSession
from os.path import join
import argparse

def get_tweet_conversas(tweet_df):
    return tweet_df.alias('tweet')\
                        .groupBy(f.to_date('created_at').alias('created_date'))\
                        .agg(
                            f.countDistinct('author_id').alias('n_tweets'),
                            f.sum('like_count').alias('n_like'),
                            f.sum('quote_count').alias('n_quote'),
                            f.sum('reply_count').alias('n_reply'),
                            f.sum('retweet_count').alias('n_retweet')
                        )\
                        .withColumn("weekday", f.date_format("created_date", "E"))
    
    
def export_delta(df, dest):
    df.coalesce(1).write.mode("overwrite").format('delta').save(dest)

def twitter_insight(spark, source, dest, process_date):
    df = spark.read.format("delta").load(source)
    tweet_df = get_tweet_conversas(df).withColumn('process_date', f.to_date(f.lit(process_date)))
    table_dest = join(dest,"{table_name}")

    export_delta(tweet_df, table_dest.format(table_name="tweets"))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Spark Twitter Transformation")

    parser.add_argument("--source", required = True)
    parser.add_argument("--dest", required = True)
    parser.add_argument("--process_date", required = True)
    
    args = parser.parse_args()

    spark = SparkSession\
    .builder\
    .getOrCreate()

    twitter_insight(spark, args.source, args.dest, args.process_date)