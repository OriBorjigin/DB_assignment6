from curses import pair_content
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Appointment:
    def __init__(self, caregiver_username, patient_username=None, vaccine_name=None, appointment_time= None):
        self.caregiver_username = caregiver_username
        self.patient_username = patient_username
        self.vaccine_name = vaccine_name
        self.appointment_time = appointment_time

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        make_appointment = "INSERT INTO Appointment VALUES (%s, %s, %s, %s)"
        try:
            cursor.execute(make_appointment, (self.caregiver_username, self.patient_username, self.vaccine_name, self.appointment_time))
            cursor.execute("SELECT SCOPE_IDENTITY()")
            result = cursor.fetchone()
            conn.commit()
            return result[0] if result else None
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    def occupy_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        decrease_availability = "DELETE FROM Availabilities WHERE Time = %s"
        
        try:
            cursor.execute(decrease_availability, d)
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()


    def release_availability(self, username, time):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        recover_availability = "UPDATE Availabilities SET Time = %s WHERE Username = %s"

        try:
            cursor.execute(recover_availability, (username, time))
            conn.commit()
        except pymssql.Error:

            raise
        finally:
            cm.close_connection()