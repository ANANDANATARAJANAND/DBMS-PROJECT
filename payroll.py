from flask import Flask, request, render_template, session, redirect, url_for, send_file
import sqlite3
from hashlib import sha256
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this in production!

def init_db():
    conn = sqlite3.connect(':memory:')
    conn.execute("PRAGMA foreign_keys = ON")
    with open('payroll.sql', 'r') as f:
        sql_script = f.read()
    try:
        conn.executescript(sql_script)
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        raise
    conn.commit()
    
    c = conn.cursor()
    # Ensure all departments exist
    departments = [(1, 'Engineering'), (2, 'HR'), (3, 'Sales'), (4, 'Marketing')]
    c.execute("SELECT COUNT(*) FROM Departments")
    if c.fetchone()[0] == 0:
        for dept_id, dept_name in departments:
            c.execute("INSERT INTO Departments (DepartmentID, DepartmentName) VALUES (?, ?)", 
                     (dept_id, dept_name))
            append_to_sql(f"INSERT INTO Departments (DepartmentID, DepartmentName) VALUES ({dept_id}, '{dept_name}')")
        conn.commit()
    
    return conn

def append_to_sql(statement):
    try:
        with open('payroll.sql', 'a') as f:
            f.write(f"{statement};\n")
    except Exception as e:
        print(f"Error appending to payroll.sql: {e}")

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = sha256(request.form['password'].encode()).hexdigest()
        conn = init_db()
        c = conn.cursor()
        c.execute("SELECT EmployeeID, Role FROM Users WHERE Username = ? AND PasswordHash = ?", 
                  (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['role'] = user[1]
            if user[1] == 'Admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('employee_dashboard'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    conn = init_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM Users WHERE Role = 'Admin'")
    admin_exists = c.fetchone()[0] > 0
    conn.close()
    
    if admin_exists:
        return render_template('login.html', error="Admin already registered. Contact support for additional admins.")
    
    if request.method == 'POST':
        try:
            employee_id = int(request.form['employee_id'])
            first_name = request.form['first_name'].replace("'", "''")
            last_name = request.form['last_name'].replace("'", "''")
            username = request.form['username'].replace("'", "''")
            password = sha256(request.form['password'].encode()).hexdigest()
            current_date = datetime.now().strftime('%Y-%m-%d')

            conn = init_db()
            c = conn.cursor()
            
            c.execute("SELECT EmployeeID FROM Employees WHERE EmployeeID = ?", (employee_id,))
            if c.fetchone():
                conn.close()
                return render_template('login.html', error="Employee ID already exists.")
            c.execute("SELECT Username FROM Users WHERE Username = ?", (username,))
            if c.fetchone():
                conn.close()
                return render_template('login.html', error="Username already taken.")

            c.execute("INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID, HireDate, JobTitle) "
                      "VALUES (?, ?, ?, ?, ?, ?)",
                      (employee_id, first_name, last_name, 1, current_date, 'Administrator'))
            c.execute("INSERT INTO Users (EmployeeID, Username, PasswordHash, Role) "
                      "VALUES (?, ?, ?, 'Admin')",
                      (employee_id, username, password))
            c.execute("INSERT INTO Salaries (SalaryID, EmployeeID, BaseSalary, EffectiveDate) "
                      "VALUES (?, ?, ?, ?)",
                      (employee_id, employee_id, 80000.00, current_date))
            c.execute("INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) "
                      "VALUES (?, ?, ?, ?, ?, ?)",
                      (employee_id, '2025-03-01', 6666.67, 1333.33, 533.33, 4800.01))
            conn.commit()

            append_to_sql(f"INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID, HireDate, JobTitle) "
                          f"VALUES ({employee_id}, '{first_name}', '{last_name}', 1, '{current_date}', 'Administrator')")
            append_to_sql(f"INSERT INTO Users (EmployeeID, Username, PasswordHash, Role) "
                          f"VALUES ({employee_id}, '{username}', '{password}', 'Admin')")
            append_to_sql(f"INSERT INTO Salaries (SalaryID, EmployeeID, BaseSalary, EffectiveDate) "
                          f"VALUES ({employee_id}, {employee_id}, 80000.00, '{current_date}')")
            append_to_sql(f"INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) "
                          f"VALUES ({employee_id}, '2025-03-01', 6666.67, 1333.33, 533.33, 4800.01)")
            
            conn.close()
            return render_template('login.html', success="Admin registered successfully. Please sign in.")
        except ValueError:
            return render_template('login.html', error="Invalid input format.")
        except sqlite3.Error as e:
            conn.close()
            return render_template('login.html', error=f"Database error: {e}")
    return render_template('admin_register.html')

@app.route('/employee_register', methods=['GET', 'POST'])
def employee_register():
    if request.method == 'POST':
        try:
            employee_id = int(request.form['employee_id'])
            first_name = request.form['first_name'].replace("'", "''")
            last_name = request.form['last_name'].replace("'", "''")
            username = request.form['username'].replace("'", "''")
            password = sha256(request.form['password'].encode()).hexdigest()
            department_id = int(request.form['department_id'])
            current_date = datetime.now().strftime('%Y-%m-%d')

            conn = init_db()
            c = conn.cursor()
            
            c.execute("SELECT EmployeeID FROM Employees WHERE EmployeeID = ?", (employee_id,))
            if c.fetchone():
                conn.close()
                return render_template('login.html', error="Employee ID already exists.")
            c.execute("SELECT Username FROM Users WHERE Username = ?", (username,))
            if c.fetchone():
                conn.close()
                return render_template('login.html', error="Username already taken.")

            c.execute("INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID, HireDate, JobTitle) "
                      "VALUES (?, ?, ?, ?, ?, ?)",
                      (employee_id, first_name, last_name, department_id, current_date, 'Employee'))
            c.execute("INSERT INTO Users (EmployeeID, Username, PasswordHash, Role) "
                      "VALUES (?, ?, ?, 'Employee')",
                      (employee_id, username, password))
            c.execute("INSERT INTO Salaries (SalaryID, EmployeeID, BaseSalary, EffectiveDate) "
                      "VALUES (?, ?, ?, ?)",
                      (employee_id, employee_id, 50000.00, current_date))
            c.execute("INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) "
                      "VALUES (?, ?, ?, ?, ?, ?)",
                      (employee_id, '2025-03-01', 4166.67, 833.33, 333.33, 3000.01))
            conn.commit()

            append_to_sql(f"INSERT INTO Employees (EmployeeID, FirstName, LastName, DepartmentID, HireDate, JobTitle) "
                          f"VALUES ({employee_id}, '{first_name}', '{last_name}', {department_id}, '{current_date}', 'Employee')")
            append_to_sql(f"INSERT INTO Users (EmployeeID, Username, PasswordHash, Role) "
                          f"VALUES ({employee_id}, '{username}', '{password}', 'Employee')")
            append_to_sql(f"INSERT INTO Salaries (SalaryID, EmployeeID, BaseSalary, EffectiveDate) "
                          f"VALUES ({employee_id}, {employee_id}, 50000.00, '{current_date}')")
            append_to_sql(f"INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) "
                          f"VALUES ({employee_id}, '2025-03-01', 4166.67, 833.33, 333.33, 3000.01)")
            
            conn.close()
            return render_template('login.html', success="Employee registered successfully. Please sign in.")
        except KeyError as e:
            return render_template('login.html', error=f"Missing field: {e}")
        except ValueError:
            return render_template('login.html', error="Invalid input format.")
        except sqlite3.Error as e:
            conn.close()
            return render_template('login.html', error=f"Database error: {e}")
    
    return render_template('login.html')

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'Admin':
        return redirect(url_for('login'))

    conn = init_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'insert_employee':
            try:
                employee_id = int(request.form['emp_id'])
                first_name = request.form['first_name'].replace("'", "''")
                last_name = request.form['last_name'].replace("'", "''")
                dept_id = int(request.form['dept_id'])
                hire_date = request.form['hire_date']
                job_title = request.form['job_title'].replace("'", "''")
                salary = float(request.form['salary'])
                password = sha256(request.form['password'].encode()).hexdigest()

                c.execute("SELECT DepartmentID FROM Departments WHERE DepartmentID = ?", (dept_id,))
                if not c.fetchone():
                    conn.close()
                    return "Invalid Department ID"

                c.execute("SELECT EmployeeID FROM Employees WHERE EmployeeID = ?", (employee_id,))
                if c.fetchone():
                    conn.close()
                    return "Employee ID already exists."

                c.execute("INSERT INTO Employees VALUES (?, ?, ?, ?, ?, ?)", 
                          (employee_id, first_name, last_name, dept_id, hire_date, job_title))
                c.execute("INSERT INTO Salaries VALUES (?, ?, ?, ?)", 
                          (employee_id, employee_id, salary, hire_date))
                c.execute("INSERT INTO Users VALUES (?, ?, ?, ?, 'Employee')", 
                          (employee_id, employee_id, first_name, password))
                conn.commit()

                append_to_sql(f"INSERT INTO Employees VALUES ({employee_id}, '{first_name}', '{last_name}', {dept_id}, '{hire_date}', '{job_title}')")
                append_to_sql(f"INSERT INTO Salaries VALUES ({employee_id}, {employee_id}, {salary}, '{hire_date}')")
                append_to_sql(f"INSERT INTO Users VALUES ({employee_id}, {employee_id}, '{first_name}', '{password}', 'Employee')")
                
            except ValueError:
                conn.close()
                return "Invalid input format"
            except sqlite3.Error as e:
                conn.close()
                return f"Database error: {e}"

        elif action == 'insert_payroll':
            try:
                employee_id = int(request.form['emp_id'])
                pay_date = request.form['pay_date']
                gross_pay = float(request.form['gross_pay'])
                taxes = gross_pay * 0.2
                deductions = gross_pay * 0.08
                net_pay = gross_pay - taxes - deductions

                c.execute("SELECT EmployeeID FROM Employees WHERE EmployeeID = ?", (employee_id,))
                if not c.fetchone():
                    conn.close()
                    return "Employee ID does not exist"

                c.execute("INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) VALUES (?, ?, ?, ?, ?, ?)",
                         (employee_id, pay_date, gross_pay, taxes, deductions, net_pay))
                conn.commit()
                append_to_sql(f"INSERT INTO Payroll (EmployeeID, PayDate, GrossPay, Taxes, Deductions, NetPay) VALUES ({employee_id}, '{pay_date}', {gross_pay}, {taxes}, {deductions}, {net_pay})")
                
            except ValueError:
                conn.close()
                return "Invalid input format"
            except sqlite3.Error as e:
                conn.close()
                return f"Database error: {e}"

        elif action == 'delete_payroll':
            try:
                payroll_id = int(request.form['payroll_id'])
                c.execute("DELETE FROM Payroll WHERE PayrollID = ?", (payroll_id,))
                conn.commit()
                append_to_sql(f"DELETE FROM Payroll WHERE PayrollID = {payroll_id}")
            except ValueError:
                conn.close()
                return "Invalid payroll ID"
            except sqlite3.Error as e:
                conn.close()
                return f"Database error: {e}"

        elif action == 'insert_attendance':
            try:
                employee_id = int(request.form['emp_id'])
                date = request.form['date']
                status = request.form['status']

                c.execute("SELECT EmployeeID FROM Employees WHERE EmployeeID = ?", (employee_id,))
                if not c.fetchone():
                    conn.close()
                    return "Employee ID does not exist"

                c.execute("INSERT INTO Attendance (EmployeeID, Date, Status) VALUES (?, ?, ?)",
                          (employee_id, date, status))
                conn.commit()
                append_to_sql(f"INSERT INTO Attendance (EmployeeID, Date, Status) VALUES ({employee_id}, '{date}', '{status}')")
                
            except ValueError:
                conn.close()
                return "Invalid input format"
            except sqlite3.Error as e:
                conn.close()
                return f"Database error: {e}"

        elif action == 'delete_attendance':
            try:
                attendance_id = int(request.form['attendance_id'])
                c.execute("DELETE FROM Attendance WHERE AttendanceID = ?", (attendance_id,))
                conn.commit()
                append_to_sql(f"DELETE FROM Attendance WHERE AttendanceID = {attendance_id}")
            except ValueError:
                conn.close()
                return "Invalid attendance ID"
            except sqlite3.Error as e:
                conn.close()
                return f"Database error: {e}"

        elif action == 'update_leave':
            try:
                request_id = int(request.form['request_id'])
                status = request.form['status']
                c.execute("UPDATE LeaveRequests SET Status = ? WHERE RequestID = ?", (status, request_id))
                conn.commit()
                append_to_sql(f"UPDATE LeaveRequests SET Status = '{status}' WHERE RequestID = {request_id}")
            except ValueError:
                conn.close()
                return "Invalid request ID"
            except sqlite3.Error as e:
                conn.close()
                return f"Database error: {e}"

    c.execute("SELECT e.*, d.DepartmentName FROM Employees e JOIN Departments d ON e.DepartmentID = d.DepartmentID")
    employees = c.fetchall()
    c.execute("SELECT * FROM Payroll")
    payrolls = c.fetchall()
    c.execute("SELECT a.*, e.FirstName, e.LastName FROM Attendance a JOIN Employees e ON a.EmployeeID = e.EmployeeID")
    attendance = c.fetchall()
    c.execute("SELECT * FROM LeaveRequests")
    leave_requests = c.fetchall()
    c.execute("SELECT FirstName FROM Employees WHERE EmployeeID = ?", (session['user_id'],))
    first_name = c.fetchone()[0]
    
    conn.close()
    return render_template('admin_dashboard.html', 
                         employees=employees, 
                         payrolls=payrolls, 
                         attendance=attendance,
                         leave_requests=leave_requests, 
                         first_name=first_name)

@app.route('/employee_dashboard', methods=['GET', 'POST'])
def employee_dashboard():
    if 'user_id' not in session or session['role'] == 'Admin':
        return redirect(url_for('login'))

    conn = init_db()
    c = conn.cursor()
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'request_leave':
            try:
                start_date = request.form['start_date']
                end_date = request.form['end_date']
                reason = request.form['reason'].replace("'", "''")
                employee_id = session['user_id']
                
                if start_date > end_date:
                    conn.close()
                    return render_template('employee_dashboard.html', error="End date must be after start date")
                
                c.execute("INSERT INTO LeaveRequests (EmployeeID, StartDate, EndDate, Reason, Status) "
                          "VALUES (?, ?, ?, ?, 'Pending')",
                          (employee_id, start_date, end_date, reason))
                conn.commit()
                
                append_to_sql(f"INSERT INTO LeaveRequests (EmployeeID, StartDate, EndDate, Reason, Status) "
                              f"VALUES ({employee_id}, '{start_date}', '{end_date}', '{reason}', 'Pending')")
                
            except ValueError:
                conn.close()
                return render_template('employee_dashboard.html', error="Invalid date format")
            except sqlite3.Error as e:
                conn.close()
                return render_template('employee_dashboard.html', error=f"Database error: {e}")

    c.execute("SELECT * FROM Payroll WHERE EmployeeID = ?", (session['user_id'],))
    payrolls = c.fetchall()
    c.execute("SELECT * FROM Attendance WHERE EmployeeID = ?", (session['user_id'],))
    attendance = c.fetchall()
    c.execute("SELECT * FROM LeaveRequests WHERE EmployeeID = ?", (session['user_id'],))
    leave_requests = c.fetchall()
    c.execute("SELECT FirstName, LastName FROM Employees WHERE EmployeeID = ?", (session['user_id'],))
    name = c.fetchone()
    conn.close()
    
    return render_template('employee_dashboard.html', 
                         payrolls=payrolls, 
                         attendance=attendance,
                         leave_requests=leave_requests, 
                         first_name=name[0], 
                         last_name=name[1])

@app.route('/generate_payscale_pdf')
def generate_payscale_pdf():
    if 'user_id' not in session or session['role'] != 'Employee':
        return redirect(url_for('login'))

    conn = init_db()
    c = conn.cursor()
    
    try:
        c.execute("SELECT e.FirstName, e.LastName, p.* FROM Employees e "
                  "JOIN Payroll p ON e.EmployeeID = p.EmployeeID "
                  "WHERE e.EmployeeID = ? ORDER BY p.PayDate DESC",
                  (session['user_id'],))
        payroll_data = c.fetchall()
        
        if not payroll_data:
            conn.close()
            return "No payroll records found", 404
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, f"Payroll Summary for {payroll_data[0][0]} {payroll_data[0][1]}")
        p.setFont("Helvetica", 12)
        p.drawString(100, 730, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        p.setFont("Helvetica-Bold", 12)
        y = 700
        headers = ["Pay Date", "Gross Pay", "Taxes", "Deductions", "Net Pay"]
        positions = [50, 150, 250, 350, 450]
        
        for header, pos in zip(headers, positions):
            p.drawString(pos, y, header)
        
        p.setFont("Helvetica", 10)
        y -= 25
        for record in payroll_data:
            p.drawString(50, y, str(record[4]))  # PayDate
            p.drawString(150, y, f"${record[5]:.2f}")  # GrossPay
            p.drawString(250, y, f"${record[6]:.2f}")  # Taxes
            p.drawString(350, y, f"${record[7]:.2f}")  # Deductions
            p.drawString(450, y, f"${record[8]:.2f}")  # NetPay
            y -= 20
        
        p.showPage()
        p.save()
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"payslip_{payroll_data[0][0]}_{payroll_data[0][1]}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        conn.close()
        return f"Error generating PDF: {str(e)}", 500
    finally:
        conn.close()

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
