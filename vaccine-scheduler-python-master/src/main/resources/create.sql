CREATE TABLE Patients(
    username varchar(255) PRIMARY KEY,
    Phone_number varchar(255),
    Salt BINARY(16),
    Hash BINARY(16)
);

CREATE TABLE Caregivers (
    Username varchar(255) PRIMARY KEY,
    Name varchar(255),
    Phone_number varchar(255),
    Salt BINARY(16),
    Hash BINARY(16)
);

CREATE TABLE Vaccines (
    Name varchar(255) PRIMARY KEY,
    Doses int
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Appointment(
    appointment_id int IDENTITY(100000,1) PRIMARY KEY,
    caregiver_username varchar(255) REFERENCES Caregivers(Username),
    patient_username varchar(255) REFERENCES Patients(username),
    vaccine_name varchar(255) REFERENCES Vaccines(Name),
    appointment_time varchar(255)
);
