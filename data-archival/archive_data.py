import csv
import os
import shutil
import time
from datetime import datetime, timedelta, timezone

import boto3
from loguru import logger
from sqlalchemy import MetaData, Table, and_, create_engine, delete, select

CSV_DIR = "/tmp/csv"


def upload_to_s3(file_path: str, bucket_name: str, s3_dir: str):
    """
    Uploads a file to an S3 bucket in a specified directory.

    :param file_path: Path to the file to upload
    :param bucket_name: Name of the S3 bucket
    :param s3_dir: Directory in the S3 bucket to upload the file to
    """

    try:
        s3_client = boto3.client("s3")
        s3_key = f"{s3_dir}/{file_path.split('/')[-1]}"
        s3_client.upload_file(file_path, bucket_name, s3_key)
        logger.info(
            f"S3 upload successful. File: {file_path}, S3 Bucket:{bucket_name}, S3 Key: {s3_key}"
        )
    except Exception as e:
        logger.error(f"S3 upload failed. Exception: {e}", exc_info=True)
        raise e


def data_to_csv(conn: str, csv_file_path: str, table_ref: Table, min_date: str, max_date: str):
    """
    Fetches data from a DB table and writes it to a CSV file.

    :param conn: Database active connection
    :param csv_file_path: CSV file path to write data in
    :param table_ref: Table reference
    :param min_date: Start date
    :param max_date: End date
    """

    offset = 0
    limit = 5000  # this can be configured
    try:
        with open(csv_file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile)
            while True:
                query = (
                    select(table_ref)
                    .where(
                        and_(
                            table_ref.c.triggered_at < max_date,
                            table_ref.c.triggered_at >= min_date,
                        )
                    )
                    .limit(limit)
                    .offset(offset)
                )

                start_time = time.time()
                result = conn.execute(query)
                rows = result.fetchall()
                # log time taken to fetch data & number of rows fetched
                logger.info(f"Rows fetched: {len(rows)} from {min_date} to {max_date}")
                logger.info(
                    f"Time taken to fetch data: {time.time() - start_time:.2f} sec"
                )

                if offset == 0 and not rows:
                    os.remove(csv_file_path)
                    logger.warning(f"Deleted empty CSV file: {csv_file_path}")
                    break

                if offset == 0 and rows:
                    csv_writer.writerow(result.keys())

                offset += limit
                if not rows:
                    logger.info(
                        f"Data exported to CSV file:{csv_file_path} successfully"
                    )
                    break
                csv_writer.writerows(rows)

                # if rows fetched are less than limit, then it's the last batch
                if len(rows) < limit:
                    break
    except Exception as e:
        logger.error(
            f"Failed to fetch and write data. Start: {min_date} & End: {max_date}. Exception: {e}"
        )
        raise e


def delete_data_from_table(conn, table_ref, table_name, min_date, max_date):
    """
    Deleting data from table between min_date and max_date

    :param conn: Database active connection
    :param table_ref: Table reference
    :param table_name: Table name from which data needs to be deleted
    :param min_date: Start date
    :param max_date: End date
    """
    try:
        start_time = time.time()
        delete_query = delete(table_ref).where(
            and_(
                table_ref.c.triggered_at < max_date,
                table_ref.c.triggered_at >= min_date,
            )
        )
        rows_deleted = conn.execute(delete_query).rowcount
        logger.info(
            f"Deleted {rows_deleted} rows from table {table_name} from {min_date} to {max_date}"
        )
        logger.info(f"Time taken to delete data: {time.time() - start_time:.2f} sec")
    except Exception as e:
        logger.error(f"Failed to delete data from table {table_name}. Exception: {e}")
        raise e


def export_data_to_s3(db_conn_string, table_name, cutoff_date, s3_bucket, s3_dir):
    """
    Exporting data (for particular dates) to csv, zip, upload to S3, and then delete data from database

    :param db_conn_string: PostgreSQL connection string
    :param schema_table_name: Name of the schema & table to query data from
    :param cutoff_date: CutOff date, data will be exported till cutoff_date
    :param s3_bucket: S3 Bucket name
    :param s3_dir: Directory in S3 bucket to upload the file to
    """
    schema, table = table_name.split(".")

    # Creating a database engine (autocommit is False by default)
    engine = create_engine(db_conn_string)
    metadata = MetaData(schema=schema)

    # Reflect the table structure from the database
    table_ref = Table(table, metadata, autoload_with=engine)

    # Creating a database connection
    with engine.connect() as conn:
        try:
            # fetch the triggered_at date of the oldest record in the table
            min_date_query = (
                select(table_ref.c.triggered_at)
                .where(table_ref.c.triggered_at < cutoff_date)
                .order_by(table_ref.c.triggered_at)
                .limit(1)
            )
            min_date_result = conn.execute(min_date_query).fetchone()

            if min_date_result is None:
                logger.warning("No data found older than cutoff date")
                return False

            min_date = datetime.combine(min_date_result[0], datetime.min.time())
            max_date = min_date + timedelta(hours=1)
            logger.info(f"SCHEDULING EXPORT FROM {min_date} TO {cutoff_date}")

            # looping hour by hour till min_date exceeds cutoff date
            while min_date < cutoff_date:
                csv_file_path = f'{CSV_DIR}/{min_date.strftime("%Y-%m-%d-%H")}.csv'

                # fetching data from table and writing it in csv
                data_to_csv(conn, csv_file_path, table_ref, min_date, max_date)

                # zipping csv file, uploading to s3, and removing files after each operation is finished.
                if os.path.exists(csv_file_path):
                    upload_to_s3(csv_file_path, s3_bucket, s3_dir)

                # deleting exported data from table
                delete_data_from_table(conn, table_ref, table_name, min_date, max_date)

                # commiting transaction as deletion of data is successful
                conn.commit()

                # changing min_date and max_date to iterate over next hour
                min_date = max_date
                max_date += timedelta(hours=1)

        except Exception as e:
            logger.exception(f"Exporting data failed. Exception: {e}")
            # rolling back data if something goes wrong
            conn.rollback()
            raise e


def export_data(rds_connection_string, schema_table_name, n_days, bucket_name, s3_dir):
    """
    Connects to an RDS PostgreSQL database, retrieves data older than specified number of days from a given table,
    exports the data to a CSV file, and stores the CSV file locally.

    :param rds_connection_string: RDS PostgreSQL connection string
    :param schema_table_name: Name of the table to query data from
    :param n_days: Number of days to filter data older than
    :param bucket_name: S3 Bucket name
    :param s3_dir: S3 Dir, files to be uploaded on
    """
    logger.info(f"N_DAYS: {n_days}")
    try:
        # Calculating cutoff date from n_days in UTC
        cutoff_date = datetime.combine(
            datetime.now(timezone.utc), datetime.min.time()
        ) - timedelta(days=n_days)
        logger.info(f"CUTOFF DATE: {cutoff_date}")

        os.makedirs(CSV_DIR, exist_ok=True)

        # exporting data from database to csv, csv -> zip, uploading zip file to S3 and deleting data from database.
        export_data_to_s3(
            rds_connection_string, schema_table_name, cutoff_date, bucket_name, s3_dir
        )

        logger.info(f"Data older than {n_days} days exported successfully")

        # removing dirs after finishing operation
        shutil.rmtree(CSV_DIR)
    except Exception as e:
        logger.exception(f"An error occurred: {e}")


def main():
    """
    Getting database creds from environment

    Exporting data (for particular dates) to csv, zip, upload to S3, and then delete data from database
    """

    DB_HOST = os.environ.get("DB_HOST")
    DB_NAME = os.environ.get("DB_NAME")
    DB_PORT = 5432
    DB_USER = os.environ.get("DB_USER")
    DB_PASSWORD = os.environ.get("DB_PASSWORD")

    S3_BUCKET = os.environ.get("S3_BUCKET")
    N_DAYS = int(os.environ.get("N_DAYS", -1))

    conn_string = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    schema_table_name = "analytics.events"
    s3_dir = f"{DB_NAME}/analytics/events"

    if N_DAYS < 0:
        logger.warning(f"Skipping archival. N_DAYS: {N_DAYS}")
    else:
        logger.info(f"Exporting {N_DAYS} ago data to csv.")
        export_data(
            conn_string,
            schema_table_name,
            N_DAYS,
            S3_BUCKET,
            s3_dir,
        )


if __name__ == "__main__":
    main()
