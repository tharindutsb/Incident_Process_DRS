from datetime import datetime, timedelta
import pymysql
from utils.database.connectSQL import get_mysql_connection
from utils.logger.logger import get_logger
from incident_process.incident_create import create_incident

logger = get_logger("process_operation_logger")

class ProcessOperation:
    def __init__(self, account_num, incident_id):
        self.system_date = datetime.now() - timedelta(minutes=1)
        self.mysql_conn = get_mysql_connection()
        self.account_num = account_num
        self.incident_id = incident_id

    def is_operation_active(self):
        """
        Check if the operation "Incident extraction from data lake" is active.
        """
        try:
            cursor = self.mysql_conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT * FROM Process_Operation 
                WHERE Operation_name = 'Incident extraction from data lake'
            """)
            operation = cursor.fetchone()
            if not operation:
                logger.error("Operation 'Incident extraction from data lake' is not active.")
                return False
            return operation
        except Exception as e:
            logger.error(f"Error checking operation status: {e}")
            return False
        finally:
            cursor.close()

    def should_run_process(self, operation):
        """
        Check if the process should run based on the conditions.
        """
        end_dtm = operation["end_dtm"]
        next_execution_dtm = operation["Next_execution_dtm"]

        if end_dtm and end_dtm <= self.system_date:
            logger.error("Process is terminated because of end date has expired.")
            return False

        if next_execution_dtm > self.system_date:
            logger.info(f"Process is scheduled to run in {next_execution_dtm} minutes.")
            return False

        return True

    def execute_process(self, operation):
        """
        Execute the process for the given account number and incident ID.
        """
        try:
            last_execution_dtm = operation["Last_execution_dtm"]
            time_period_start = last_execution_dtm
            time_period_end = self.system_date

            # Fetch accounts from debt_cust_detail within the time period
            cursor = self.mysql_conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT DISTINCT ACCOUNT_NUM 
                FROM debt_cust_detail 
                WHERE ACCOUNT_NUM = %s AND LOAD_DATE BETWEEN %s AND %s
            """, (self.account_num, time_period_start, time_period_end))
            accounts = cursor.fetchall()

            for account in accounts:
                account_num = account["ACCOUNT_NUM"]
                incident = create_incident(account_num, self.incident_id)
                success = incident.process_incident()

                if success:
                    logger.info(f"Incident processed successfully for account: {account_num}")
                else:
                    logger.error(f"Failed to process incident for account: {account_num}")

            # Update Process_Operation table on success
            cursor.execute("""
                UPDATE Process_Operation 
                SET Last_execution_dtm = %s, 
                    Next_execution_dtm = %s, 
                    Process_Operation_Sequence = Process_Operation_Sequence + 1
                WHERE Operation_name = 'Incident extraction from data lake'
            """, (self.system_date, self.system_date + timedelta(minutes=60)))
            self.mysql_conn.commit()
            logger.info("Process_Operation table updated successfully.")
        except Exception as e:
            logger.error(f"Error executing process: {e}")
        finally:
            cursor.close()

    def run(self):
        """
        Main method to run the process.
        """
        operation = self.is_operation_active()
        if not operation:
            return

        if self.should_run_process(operation):
            self.execute_process(operation)

    def close_connection(self):
        """
        Close the MySQL connection.
        """
        if self.mysql_conn:
            self.mysql_conn.close()

