"""Structured Streaming job to consume crypto prices from Kafka."""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import DoubleType, StringType, StructField, StructType

KAFKA_BOOTSTRAP = "localhost:9092"
TOPIC = "crypto_prices"


def main() -> None:
    spark = (
        SparkSession.builder.appName("CryptoPriceStreaming")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # Schema matches the JSON payload produced by the Kafka producer.
    schema = StructType(
        [
            StructField("symbol", StringType(), False),
            StructField("price", DoubleType(), False),
            StructField("event_time", StringType(), False),
            StructField("source", StringType(), False),
        ]
    )

    # Read the Kafka topic as a streaming source.
    raw_stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    parsed_stream = (
        raw_stream.select(from_json(col("value").cast("string"), schema).alias("data"))
        .select("data.*")
    )

    # Print to console for quick validation during development.
    query = (
        parsed_stream.writeStream.format("console")
        .outputMode("append")
        .option("truncate", "false")
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
