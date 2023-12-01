from ast import Not
from math import pi
from os import name
import select
import time
from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointment import Appointment
from model.Main_menu_printing import main_menu
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    # create_caregiver <username> <phone number> <password> 
    # check 1: the length for tokens need to be exactly 5 to include all information (with the operation name)
    if len(tokens) != 4:
        print("-"*50)
        print()
        print("Failed to create user.")
        print("Please enter all required fields as shown below:")
        print("1. create_patient")
        print("2. username")
        print("3. phone number")
        print("4. password")
        print()
        print("-"*50)
        
        return

    username = tokens[1]
    phone_number = tokens[2]
    password = tokens[3]



    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        
        print("-"*50)
        print()
        print("Username taken, try again!")
        print()
        print("-"*50)
        return
   
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    patient = Patient(username, phone_number, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("-"*50)
    print()
    print("Created user ", username)
    print()
    print("-"*50)
    main_menu.print_menu()

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <name> <phone number> <password>
    # check 1: the length for tokens need to be exactly 5 to include all information (with the operation name)
    if len(tokens) != 5:
        
        print("-"*50)
        print()
        print("Failed to create user.")
        print("Please enter all required fields as shown below:")
        print("1. create_patient")
        print("2. username")
        print("3. name")
        print("4. phone number")
        print("5. password")
        print()
        print("-"*50)
        return

    username = tokens[1]
    name = tokens[2]
    phone_number = tokens[3]
    password = tokens[4]



    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, name, phone_number, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    
    print("-"*50)
    print()
    print("Created user ", username)
    print()
    print("-"*50)
    main_menu.print_menu()


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("-"*50)
        print()
        print("User already logged in.")
        print()
        print("-"*50)
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("-"*50)
        print()
        print("Login failed.")
        print()
        print("-"*50)
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("-"*50)
        print()
        print("Logged in as: " + username)
        print()
        print("-"*50)
        main_menu.print_menu()
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("-"*50)
        print()
        print("Login failed.")
        print()
        print("-"*50)
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("-"*50)
        print()
        print("Logged in as: " + username)
        print()
        print("-"*50)
        main_menu.print_menu()
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    global current_caregiver, current_patient
    current_user = current_caregiver if current_caregiver else current_patient
    if current_user is None:
        print("-"*50)
        print()
        print("No user is currently logged in")
        print()
        print("-"*50)
        return
    
    if len(tokens) != 2:
        print("Invalid input")
        print("Please enter all required fields")
        return
    
    time = tokens[1]

    try:
        # The format of date is MM-DD-YYYY
        valid_time = datetime.datetime.strptime(time, "%m-%d-%Y").date()
    except ValueError:
        print("Invalid date format. Please use MM-DD-YYYY (09-01-2023)")
        return

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        select_query = "SELECT c.username, c.name, c.phone_number FROM Caregivers AS c, Availabilities AS a WHERE c.username = a.username AND a.time = %s ORDER BY c.username"
        select_query_vaccine_availability = "SELECT * FROM Vaccines"
        cursor.execute(select_query, (valid_time))
        caregivers = cursor.fetchall()
        cursor.execute(select_query_vaccine_availability)
        vaccine_availability = cursor.fetchall()

        if caregivers:
            print("-"*50)
            print()
            print("Caregivers:", caregivers[0], "available on", time, ":")
            print("name | phone number")
            for username, name, phone_number in caregivers:
                print(name, phone_number)
            print()
            print("-"*50)
            print("Vaccine aviliabilities are as follows:")
            print("Vaccine | Availability")
            for vaccine_name, vaccine_doses in vaccine_availability:
                print("-"*50)
                print()
                print(vaccine_name, vaccine_doses)
                print()
                print("-"*50)
                main_menu.print_menu()

        else:
            print("-"*50)
            print()
            print("No caregiver available on", time, ". Please try another date.")
            print()
            print("-"*50)
            main_menu.print_menu()
    except pymssql.Error as e:
        print("Failed to query the database.")
        print("Db-Error:", e)
    finally:
        cm.close_connection()
    return False


def reserve(tokens):
    global current_patient, current_caregiver

    if len(tokens) != 5:
        print("-"*50)
        print()
        print("Please try again, make sure you enter all required fields:")
        print("1. Caregiver's username")
        print("2. Patient's username")
        print("3. Vaccine name")
        print("4. Appointment time")
        print("Note: Appointment can be made one at a time")
        print("One dose per time")
        print()
        print("-"*50)
        return

    caregiver_username = tokens[1]
    patient_username = tokens[2]
    vaccine_name = tokens[3]
    appointment_time = tokens[4]

    current_user = current_caregiver if current_caregiver else current_patient
    if current_user is not current_patient:
        print("Please login as patient first")


    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        check_availability_query = "SELECT * FROM Caregivers AS c, Availabilities AS a WHERE c.Username = a.Username AND c.Username = %s AND a.Time = %s"
        cursor.execute(check_availability_query, (caregiver_username, appointment_time))
        if cursor.fetchone() is None:
            print("Caregiver is not available on this date")
            return

        check_vaccine_avaibility_query = "SELECT Doses FROM Vaccines WHERE Name = %s"
        cursor.execute(check_vaccine_avaibility_query, vaccine_name)
        vaccine_doses = cursor.fetchone()
        if not vaccine_doses or vaccine_doses[0] < 1:
            print("Insufficient vaccine doses available")
            return

        appointment = Appointment(caregiver_username, patient_username, vaccine_name, appointment_time)
        appointment_id = appointment.save_to_db()
        appointment.occupy_availability(appointment_time) 

        print("-"*50)
        print()
        print("Appointment made successfully by", current_user.username)
        print("Appointment ID:", appointment_id)
        print("Please remember this ID for future appointment cancelation")
        print()
        print("-"*50)
        main_menu.print_menu()

        # Decrease vaccine doses
        vaccine_decrease = Vaccine(vaccine_name, vaccine_doses[0])
        vaccine_decrease.decrease_available_doses(1)
        

    except pymssql.Error as e:  
        print("Failed to create appointment.")
        print("Please try again")
        print("Db-Error:", e)
    except Exception as e:
        print("Failed to create appointment.")
        print("Please try again")
        print(e)
    finally:
        cm.close_connection()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("-"*50)
    print()
    print("Availability uploaded!")
    print()
    print("-"*50)
    main_menu.print_menu()


def cancel(tokens):
    global current_patient, current_caregiver
    if len(tokens) != 4:
        print("-"*50)
        print()
        print("Please enter all required fields")
        print("1. Appointment ID (6 digits number)")
        print("2. Appointment Time (MM-DD-YYYY)")
        print("3. Caregiver name")
        print("Make sure you have the correct information entered")
        print()
        print("-"*50)
        return

    appointment_id = tokens[1]
    caregiver_name = tokens[2]
    appointment_time = tokens[3]

    current_user = current_caregiver if current_caregiver else current_patient
    if current_user is None:
        print("Please log in before you cancel the appointment")
        return

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        select_query = "SELECT vaccine_name FROM Appointment WHERE appointment_id = %s AND appointment_time = %s"
        cursor.execute(select_query, (appointment_id, appointment_time))
        result = cursor.fetchone()
        if not result:
            print("No such appointment found.")
            return

        vaccine_name = result['vaccine_name']

        delete_query = "DELETE FROM Appointment WHERE appointment_id = %s AND appointment_time = %s"
        cursor.execute(delete_query, (appointment_id, appointment_time))

        select_quantity_query = "SELECT Doses FROM Vaccines WHERE Name = %s"
        cursor.execute(select_quantity_query, vaccine_name)
        vaccine_quantity_result = cursor.fetchone()
        if not vaccine_quantity_result:
            print("Failed to retrieve vaccine quantity.")
            return

        vaccine_quantity = vaccine_quantity_result['Doses']
        vaccine = Vaccine(vaccine_name, vaccine_quantity)
        vaccine.increase_available_doses(1)

        release_availability = Appointment(caregiver_name)
        release_availability.release_availability(caregiver_name, appointment_time)

        conn.commit()
        
        print("-"*50)
        print()
        print("Appointment", appointment_id, "cancellation success")
        print()
        print("-"*50)
        main_menu.print_menu()

    except pymssql.Error as e:
        print("Database error:", e)
    finally:
        cm.close_connection()


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("-"*50)
    print()
    print("Doses updated!")
    print()
    print("-"*50)
    main_menu.print_menu()



def show_appointments(tokens):
    global current_caregiver, current_patient
    current_user = current_caregiver if current_caregiver else current_patient
    if current_user is None:
        print("Please log in before you check your appointment.")
        return
    if len(tokens) != 1:
        print("Incorrect command. Just enter 'show_appointments' to view your appointments.")
        return

    try:
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        if current_user == current_caregiver:
            select_query = "SELECT * FROM Appointment WHERE caregiver_username = %s"
        else:
            select_query = "SELECT * FROM Appointment WHERE patient_username = %s"

        cursor.execute(select_query, current_user.username)
        appointments = cursor.fetchall()

        if appointments:
            print()
            print("-"*50)
            print("User:", current_user.username, "has the following appointments:")
            for appointment in appointments:
                print(appointment)
            print()
            print("-"*50)
            main_menu.print_menu()

        else:
            print()
            print("-"*50)
            print("No appointments found for user:", current_user.username)
            print()
            print("-"*50)
            main_menu.print_menu()

    except pymssql.Error as e:
        print("Database error:", e)
    finally:
        cm.close_connection()


def logout(tokens):
    global current_patient, current_caregiver

    if current_patient is None and current_caregiver is None:
        print()
        print("-"*50)
        print("No user is currently logged in.")
        print()
        print("-"*50)
        main_menu.print_menu()
        return

    if current_patient is not None:
        print()
        print("-"*50)
        print("Logging out patient:", current_patient.username)
        print()
        print("-"*50)
        main_menu.print_menu()
        current_patient = None

    if current_caregiver is not None:
        print()
        print("-"*50)
        print("Logging out caregiver:", current_caregiver.username)
        print()
        print("-"*50)
        main_menu.print_menu()
        current_caregiver = None


def start():
    stop = False
    print()
    print("-"*50)
    print(" *** Please enter one of the following commands *** ")
    print("-"*50)
    print("> create_patient <username> <phone number> <password>")  # //TODO: implement create_patient (Part 1)
    print("-"*50)
    print("> create_caregiver <username> <name> <phone number> <password>")
    print("-"*50)
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("-"*50)
    print("> login_caregiver <username> <password>")
    print("-"*50)
    print("> search_caregiver_schedule <date(MM-DD-YYYY)>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("  -- Note: caregiver's name is useful when you cancel the appointment, please write it down --")
    print("-"*50)
    print("> reserve <caregiver username> <patient username> <vaccine> <date(MM-DD-YYYY)>")  # // TODO: implement reserve (Part 2)
    print("  -- Note: please remember your appointment ID and keep it safe, it can be used for appointment cancellation --")
    print("-"*50)
    print("> upload_availability <date(MM-DD-YYYY)>")
    print("  -- Note: please enter one date at a time; and you can only upload login account availability --")
    print("-"*50)
    print("> cancel <appointment id> <caregiver name> <appointment time(MM-DD-YYYY)>")  # // TODO: implement cancel (extra credit)
    print("-"*50)
    print("> add_doses <vaccine> <number>")
    print("-"*50)
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("-"*50)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("-"*50)
    print("> Quit")
    print("-"*50)
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
