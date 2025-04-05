CREATE TABLE Departments (
    DepartmentID INTEGER PRIMARY KEY,
    DepartmentName TEXT NOT NULL
);

CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    DepartmentID INTEGER,
    HireDate TEXT,
    JobTitle TEXT,
    FOREIGN KEY (DepartmentID) REFERENCES Departments(DepartmentID)
);

CREATE TABLE Salaries (
    SalaryID INTEGER PRIMARY KEY,
    EmployeeID INTEGER,
    BaseSalary REAL NOT NULL,
    EffectiveDate TEXT,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

CREATE TABLE Payroll (
    PayrollID INTEGER PRIMARY KEY,
    EmployeeID INTEGER,
    PayDate TEXT,
    GrossPay REAL,
    Taxes REAL,
    Deductions REAL,
    NetPay REAL,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

CREATE TABLE Users (
    UserID INTEGER PRIMARY KEY,
    EmployeeID INTEGER,
    Username TEXT UNIQUE,
    PasswordHash TEXT,
    Role TEXT DEFAULT 'Employee',
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

CREATE TABLE Attendance (
    AttendanceID INTEGER PRIMARY KEY ,
    EmployeeID INTEGER,
    Date TEXT,
    Status TEXT,
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);

CREATE TABLE LeaveRequests (
    RequestID INTEGER PRIMARY KEY,
    EmployeeID INTEGER,
    StartDate TEXT,
    EndDate TEXT,
    Reason TEXT,
    Status TEXT DEFAULT 'Pending',
    FOREIGN KEY (EmployeeID) REFERENCES Employees(EmployeeID)
);
INSERT INTO Departments (DepartmentID, DepartmentName) VALUES (1, 'Engineering');
INSERT INTO Departments (DepartmentID, DepartmentName) VALUES (2, 'HR');
INSERT INTO Departments (DepartmentID, DepartmentName) VALUES (3, 'Sales');
INSERT INTO Departments (DepartmentID, DepartmentName) VALUES (4, 'Marketing');
INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID, HireDate, JobTitle) VALUES (101, 'AJAY', 'KUMAR', 1, '2025-03-30', 'Administrator');
INSERT INTO Users (EmployeeID, Username, PasswordHash, Role) VALUES (101, 'user', '78a72bcb9c0f3714c0924cf037d407ec7ee513ac20c42df073db98e318d3a979', 'Admin');
INSERT INTO Salaries (SalaryID, EmployeeID, BaseSalary, EffectiveDate) VALUES (101, 101, 80000.00, '2025-03-30');
INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) VALUES (101, '2025-03-01', 6666.67, 1333.33, 533.33, 4800.01);
INSERT INTO Employees VALUES (102, 'ANAND', 'KUMAR', 1, '2025-03-24', 'EMPLOYEE');
INSERT INTO Salaries VALUES (102, 102, 12000.0, '2025-03-24');
INSERT INTO Users VALUES (102, 102, 'ANAND', '09f20401f06d506fbd8c9079420dcc050f1f8ec810ae2c915d57063aca612778', 'Employee');
INSERT INTO Attendance (EmployeeID, Date, Status) VALUES (101, '2025-03-30', 'Present');
INSERT INTO Attendance (EmployeeID, Date, Status) VALUES (102, '2025-03-29', 'Present');

                    INSERT INTO LeaveRequests 
                    (EmployeeID, StartDate, EndDate, Reason, Status) 
                    VALUES (102, '2025-03-31', '2025-03-31', 'SICK

', 'Pending')
                ;
UPDATE LeaveRequests SET Status = 'Approved' WHERE RequestID = 1;
INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) VALUES (102, '2025-03-31', 120000.0, 24000.0, 9600.0, 86400.0);

INSERT INTO Employees VALUES (103, 'JOHN', 'ADAMS', 2, '2025-03-31', 'HR Manager');
INSERT INTO Salaries VALUES (103, 103, 200000.0, '2025-03-31');
INSERT INTO Users VALUES (103, 103, 'JOHN', '4d41a893f4d341b4637187803907dbc72d056d35f6024940aef770e3786f4461', 'Employee');
INSERT INTO Employees VALUES (104, 'VIJAY', 'PRANAV', 3, '2025-04-05', 'SALES MANAGER');
INSERT INTO Salaries VALUES (104, 104, 250000.0, '2025-04-05');
INSERT INTO Users VALUES (104, 104, 'VIAJY', '7301c5aebf48c5bf0aec05516e72aa59297bf395b82142104df3ad421d6d5f52', 'Employee');
INSERT INTO Employees VALUES (105, 'ARUL', 'JOEL', 3, '2025-03-31', 'UI/UX DESINGNER');
INSERT INTO Salaries VALUES (105, 105, 100000.0, '2025-03-31');
INSERT INTO Users VALUES (105, 105, 'ARUL', 'ab6f9f9eae4811f010979e43b9da96f5a1693d320543d8e6d39742884884a4c0', 'Employee');
INSERT INTO Attendance (EmployeeID, Date, Status) VALUES (101, '2025-03-30', 'Present');
DELETE FROM Attendance WHERE AttendanceID = 3;
INSERT INTO Attendance (EmployeeID, Date, Status) VALUES (103, '2025-03-30', 'Present');

                    INSERT INTO LeaveRequests 
                    (EmployeeID, StartDate, EndDate, Reason, Status) 
                    VALUES (103, '2025-03-31', '2025-03-31', 'I AM ON DUTY ', 'Pending')
                ;
INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) VALUES (103, '2025-03-30', 120000.0, 24000.0, 9600.0, 86400.0);
INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID, HireDate, JobTitle) VALUES (107, 'kiyothaka', 'abc', 1, '2025-04-03', 'Employee');
INSERT INTO Users (EmployeeID, Username, PasswordHash, Role) VALUES (107, 'ki', 'ad0db94891e947bc733074d651b657f5aa4c3b4e681a8f8f5e9fc696c5d7d9bd', 'Employee');
INSERT INTO Salaries (SalaryID, EmployeeID, BaseSalary, EffectiveDate) VALUES (107, 107, 50000.00, '2025-04-03');
INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) VALUES (107, '2025-03-01', 4166.67, 833.33, 333.33, 3000.01);
INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) VALUES (107, '2025-04-04', 30000.0, 6000.0, 2400.0, 21600.0);
DELETE FROM Payroll WHERE PayrollID = 4;
INSERT INTO LeaveRequests (EmployeeID, StartDate, EndDate, Reason, Status) VALUES (107, '2025-04-04', '2025-04-05', 'hskjgkkkjghfjfjh', 'Pending');
UPDATE LeaveRequests SET Status = 'Approved' WHERE RequestID = 3;
