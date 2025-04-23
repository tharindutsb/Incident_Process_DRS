from logger_singleton import SingletonLogger
from oracle_connection import OracleConnectionSingleton

def main():
    SingletonLogger.configure()

    logger = SingletonLogger.get_logger('appLogger')
    logger.info("App started")

    # db = OracleConnectionSingleton()
    # conn = db.get_connection()

    # if conn:
    #     logger.info("Ready to run queries...")
    #     cursor = conn.cursor()
    #     cursor.execute("SELECT sysdate FROM dual")
    #     print("Current DB Time:", cursor.fetchone())
        # cursor.execute("SELECT * FROM YOUR_TABLE")
        # rows = cursor.fetchall()
        # for row in rows:
        #     print(row)

    # db.close_connection()
    # logger.info("App finished")

    with OracleConnectionSingleton() as conn:
        if conn:
            logger.info("Ready to run queries...")
            cursor = conn.cursor()
            cursor.execute("SELECT sysdate FROM dual")
            print("Current DB Time:", cursor.fetchone())

            cursor.execute("SELECT * FROM PROCESS_OPERATION")
            rows = cursor.fetchall()

            for row in rows:
                print(row)

            logger.info(f"Retrieved {len(rows)} rows from PROCESS_OPERATION.")

if __name__ == "__main__":
    main()
