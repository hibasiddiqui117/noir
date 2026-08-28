from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import os

from .database import engine, get_db, create_tables, test_connection
from .models import Employee
from .schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    EmployeeListResponse, EmployeeStats, DepartmentStats
)
from . import crud

# Test database connection on startup
print("\n" + "="*50)
print("🚀 Starting FastAPI Application")
print("="*50)

if test_connection():
    print("✅ Database connection established")
    create_tables()
else:
    print("❌ Database connection failed!")
    print("="*50 + "\n")

app = FastAPI(
    title="Employee Portal API",
    description="Complete Employee Management System with CRUD, Search, and Analytics",
    version=os.getenv("APP_VERSION", "1.0.0")
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROOT ENDPOINT ====================
@app.get("/")
def root():
    return {
        "message": "Welcome to Employee Portal API",
        "status": "running",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "endpoints": {
            "employees": "/employees",
            "employees_by_id": "/employees/{id}",
            "departments": "/departments",
            "stats": "/stats",
            "search": "/search",
            "recent_hires": "/recent-hires",
            "docs": "/docs"
        }
    }

# ==================== HEALTH CHECK ====================
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        count = db.query(Employee).count()
        return {
            "status": "healthy",
            "database": "connected",
            "employee_count": count
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

# ==================== CREATE EMPLOYEE ====================
@app.post("/employees/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    """Create a new employee"""
    # Check if employee_id already exists
    existing = crud.get_employee_by_emp_id(db, employee.employee_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with ID {employee.employee_id} already exists"
        )
    
    # Check if email already exists
    existing_email = crud.get_employee_by_email(db, employee.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with email {employee.email} already exists"
        )
    
    # Create employee
    db_employee = crud.create_employee(db, employee)
    
    return EmployeeResponse(
        id=db_employee.id,
        employee_id=db_employee.employee_id,
        first_name=db_employee.first_name,
        last_name=db_employee.last_name,
        email=db_employee.email,
        department=db_employee.department,
        position=db_employee.position,
        salary=db_employee.salary,
        hire_date=db_employee.hire_date,
        status=db_employee.status
    )

# ==================== GET ALL EMPLOYEES ====================
@app.get("/employees/", response_model=EmployeeListResponse)
def get_employees(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = Query(None, regex="^(id|employee_id|first_name|last_name|salary|hire_date)$"),
    sort_desc: bool = False,
    db: Session = Depends(get_db)
):
    """Get all employees with pagination, filtering, and sorting"""
    employees = crud.get_employees(
        db, skip=skip, limit=limit, 
        search=search, department=department, 
        status=status, sort_by=sort_by, sort_desc=sort_desc
    )
    
    total = crud.get_employee_count(db, search=search, department=department, status=status)
    
    # Convert employees to response format
    employee_responses = []
    for emp in employees:
        employee_responses.append(
            EmployeeResponse(
                id=emp.id,
                employee_id=emp.employee_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                department=emp.department,
                position=emp.position,
                salary=emp.salary,
                hire_date=emp.hire_date,
                status=emp.status,
                created_at=emp.created_at,
                updated_at=emp.updated_at
            )
        )
    
    return {
        "total": total,
        "employees": employee_responses
    }

# ==================== GET EMPLOYEE BY ID ====================
@app.get("/employees/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    """Get a specific employee by ID"""
    db_employee = crud.get_employee(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return EmployeeResponse(
        id=db_employee.id,
        employee_id=db_employee.employee_id,
        first_name=db_employee.first_name,
        last_name=db_employee.last_name,
        email=db_employee.email,
        department=db_employee.department,
        position=db_employee.position,
        salary=db_employee.salary,
        hire_date=db_employee.hire_date,
        status=db_employee.status,
        created_at=db_employee.created_at,
        updated_at=db_employee.updated_at
    )

# ==================== UPDATE EMPLOYEE - FIXED ====================
@app.put("/employees/{employee_id}", response_model=EmployeeResponse)
def update_employee(employee_id: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):
    """Update an employee - only update provided fields"""
    # Check if employee exists
    db_employee = crud.get_employee(db, employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # If employee_id is being updated, check it doesn't conflict
    if employee.employee_id:
        existing = crud.get_employee_by_emp_id(db, employee.employee_id)
        if existing and existing.id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with ID {employee.employee_id} already exists"
            )
    
    # If email is being updated, check it doesn't conflict
    if employee.email:
        existing_email = crud.get_employee_by_email(db, employee.email)
        if existing_email and existing_email.id != employee_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with email {employee.email} already exists"
            )
    
    # Update employee
    updated_employee = crud.update_employee(db, employee_id, employee)
    
    return EmployeeResponse(
        id=updated_employee.id,
        employee_id=updated_employee.employee_id,
        first_name=updated_employee.first_name,
        last_name=updated_employee.last_name,
        email=updated_employee.email,
        department=updated_employee.department,
        position=updated_employee.position,
        salary=updated_employee.salary,
        hire_date=updated_employee.hire_date,
        status=updated_employee.status,
        created_at=updated_employee.created_at,
        updated_at=updated_employee.updated_at
    )

# ==================== DELETE EMPLOYEE ====================
@app.delete("/employees/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    """Delete an employee"""
    if not crud.delete_employee(db, employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return None

# ==================== GET DEPARTMENTS ====================
@app.get("/departments/")
def get_departments(db: Session = Depends(get_db)):
    """Get all departments with employee counts"""
    stats = crud.get_department_stats(db)
    return {
        "departments": stats,
        "total_departments": len(stats)
    }

# ==================== GET EMPLOYEE STATISTICS ====================
@app.get("/stats/", response_model=EmployeeStats)
def get_stats(db: Session = Depends(get_db)):
    """Get overall employee statistics"""
    return crud.get_overall_stats(db)

# ==================== SEARCH EMPLOYEES ====================
@app.get("/search/", response_model=List[EmployeeResponse])
def search_employees(query: str = Query(..., min_length=2), db: Session = Depends(get_db)):
    """Search employees by name, department, or position"""
    if len(query) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Search query must be at least 2 characters"
        )
    employees = crud.search_employees(db, query)
    
    employee_responses = []
    for emp in employees:
        employee_responses.append(
            EmployeeResponse(
                id=emp.id,
                employee_id=emp.employee_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                department=emp.department,
                position=emp.position,
                salary=emp.salary,
                hire_date=emp.hire_date,
                status=emp.status,
                created_at=emp.created_at,
                updated_at=emp.updated_at
            )
        )
    
    return employee_responses

# ==================== GET RECENT HIRES ====================
@app.get("/recent-hires/", response_model=List[EmployeeResponse])
def get_recent_hires(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Get employees hired in the last N days"""
    employees = crud.get_recent_hires(db, days)
    
    employee_responses = []
    for emp in employees:
        employee_responses.append(
            EmployeeResponse(
                id=emp.id,
                employee_id=emp.employee_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                department=emp.department,
                position=emp.position,
                salary=emp.salary,
                hire_date=emp.hire_date,
                status=emp.status,
                created_at=emp.created_at,
                updated_at=emp.updated_at
            )
        )
    
    return employee_responses

# ==================== GET EMPLOYEES BY DEPARTMENT ====================
@app.get("/departments/{department}/employees", response_model=List[EmployeeResponse])
def get_employees_by_department(department: str, db: Session = Depends(get_db)):
    """Get all employees in a specific department"""
    employees = crud.get_employees_by_department(db, department)
    if not employees:
        raise HTTPException(
            status_code=404, 
            detail=f"No employees found in department: {department}"
        )
    
    employee_responses = []
    for emp in employees:
        employee_responses.append(
            EmployeeResponse(
                id=emp.id,
                employee_id=emp.employee_id,
                first_name=emp.first_name,
                last_name=emp.last_name,
                email=emp.email,
                department=emp.department,
                position=emp.position,
                salary=emp.salary,
                hire_date=emp.hire_date,
                status=emp.status,
                created_at=emp.created_at,
                updated_at=emp.updated_at
            )
        )
    
    return employee_responses

# ==================== CHATBOT ENDPOINT ====================
@app.post("/chatbot/")
def chatbot_query(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Natural language chatbot for employee queries"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["add", "create", "new", "insert"]):
        if "employee" in query_lower:
            return handle_add_employee(query, db)
    
    if any(word in query_lower for word in ["find", "search", "show", "list", "get"]):
        return handle_search_employee(query, db)
    
    if "department" in query_lower:
        return handle_department_query(query, db)
    
    if any(word in query_lower for word in ["count", "total", "how many", "stats", "statistics"]):
        return handle_statistics(db)
    
    if "recent" in query_lower or "new hire" in query_lower:
        return handle_recent_hires(query, db)
    
    return {
        "response": "🤖 I can help you with employee queries. Try asking:\n"
                   "• 'Add a new employee named John Doe in Engineering'\n"
                   "• 'Find employees in Marketing'\n"
                   "• 'Show me all employees'\n"
                   "• 'How many employees do we have?'\n"
                   "• 'Who was hired recently?'\n"
                   "• 'What are the department statistics?'"
    }

# ==================== CHATBOT HELPER FUNCTIONS ====================
def handle_add_employee(query: str, db: Session):
    """Extract employee information from natural language and add to database"""
    import re
    from datetime import date
    
    name_match = re.search(r'(?:named|name)?\s*([A-Z][a-z]+)\s+([A-Z][a-z]+)', query)
    if not name_match:
        return {"response": "❌ I couldn't understand the employee name. Please provide first and last name."}
    
    first_name = name_match.group(1)
    last_name = name_match.group(2)
    
    department = "Engineering"
    position = "Developer"
    salary = 70000.0
    hire_date = date.today()
    
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "IT", "Operations", "Legal"]
    for dept in departments:
        if dept.lower() in query.lower():
            department = dept
            break
    
    positions = ["Developer", "Manager", "Analyst", "Engineer", "Specialist", "Director", 
                 "Coordinator", "Consultant", "Architect", "Admin"]
    for pos in positions:
        if pos.lower() in query.lower():
            position = pos
            break
    
    salary_match = re.search(r'(\d+[,.]?\d*)\s*(?:k|thousand|salary)', query, re.IGNORECASE)
    if salary_match:
        try:
            salary = float(salary_match.group(1).replace(',', ''))
            if "k" in query or "thousand" in query:
                salary *= 1000
        except:
            pass
    
    employee_data = {
        "employee_id": f"EMP{str(db.query(Employee).count() + 1).zfill(3)}",
        "first_name": first_name,
        "last_name": last_name,
        "email": f"{first_name.lower()}.{last_name.lower()}@company.com",
        "department": department,
        "position": position,
        "salary": salary,
        "hire_date": hire_date
    }
    
    try:
        new_employee = crud.create_employee(db, employee_data)
        return {
            "response": f"✅ Employee {first_name} {last_name} added successfully!\n"
                       f"📧 Email: {new_employee.email}\n"
                       f"🏢 Department: {department}\n"
                       f"💼 Position: {position}\n"
                       f"💰 Salary: ${salary:,.2f}",
            "employee": new_employee.to_dict()
        }
    except Exception as e:
        return {"response": f"❌ Failed to add employee: {str(e)}"}

def handle_search_employee(query: str, db: Session):
    """Search for employees based on natural language query"""
    import re
    
    name_match = re.search(r'(?:named|name)?\s*([A-Z][a-z]+)(?:\s+([A-Z][a-z]+))?', query)
    if name_match:
        first_name = name_match.group(1)
        employees = crud.search_employees(db, first_name)
        if employees:
            return {
                "response": f"✅ Found {len(employees)} employee(s) matching '{first_name}':",
                "employees": [emp.to_dict() for emp in employees]
            }
    
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "IT", "Operations", "Legal"]
    for dept in departments:
        if dept.lower() in query.lower():
            employees = crud.get_employees_by_department(db, dept)
            if employees:
                return {
                    "response": f"✅ Found {len(employees)} employees in {dept} department:",
                    "employees": [emp.to_dict() for emp in employees]
                }
    
    employees = crud.get_employees(db, limit=5)
    return {
        "response": f"ℹ️ No employees found matching your query. Here are some employees (showing 5):",
        "employees": [emp.to_dict() for emp in employees]
    }

def handle_department_query(query: str, db: Session):
    """Handle department-specific queries"""
    departments = ["Engineering", "Marketing", "Sales", "HR", "Finance", "IT", "Operations", "Legal"]
    
    for dept in departments:
        if dept.lower() in query.lower():
            employees = crud.get_employees_by_department(db, dept)
            stats = crud.get_department_stats(db)
            dept_stats = next((s for s in stats if s['department'] == dept), None)
            
            response = f"📊 Department: {dept}\n"
            response += f"👥 Total Employees: {len(employees)}\n"
            if dept_stats:
                response += f"💰 Average Salary: ${dept_stats['avg_salary']:,.2f}\n"
                response += f"📈 Salary Range: ${dept_stats['min_salary']:,.2f} - ${dept_stats['max_salary']:,.2f}"
            
            return {
                "response": response,
                "employees": [emp.to_dict() for emp in employees],
                "statistics": dept_stats
            }
    
    return {"response": "❌ Please specify a valid department (Engineering, Marketing, Sales, HR, Finance, IT, Operations, Legal)"}

def handle_statistics(db: Session):
    """Return statistics about employees"""
    stats = crud.get_overall_stats(db)
    
    response = "📊 Employee Statistics:\n"
    response += f"• Total Employees: {stats['total_employees']}\n"
    response += f"• Active Employees: {stats['active_employees']}\n"
    response += f"• Inactive Employees: {stats['inactive_employees']}\n"
    response += f"• Average Salary: ${stats['avg_salary_overall']:,.2f}\n\n"
    response += "📈 Department Breakdown:\n"
    
    for dept in stats['departments']:
        response += f"  • {dept['department']}: {dept['count']} employees, "
        response += f"Avg Salary: ${dept['avg_salary']:,.2f}\n"
    
    return {
        "response": response,
        "statistics": stats
    }

def handle_recent_hires(query: str, db: Session):
    """Handle recent hires query"""
    import re
    
    days_match = re.search(r'(\d+)\s*(?:days?|day)', query)
    days = int(days_match.group(1)) if days_match else 30
    
    employees = crud.get_recent_hires(db, days)
    
    if employees:
        response = f"🆕 Employees hired in the last {days} days:\n"
        for emp in employees[:10]:
            response += f"  • {emp.first_name} {emp.last_name} - {emp.department} "
            response += f"(Hired: {emp.hire_date.strftime('%Y-%m-%d')})\n"
        
        if len(employees) > 10:
            response += f"\n... and {len(employees) - 10} more"
        
        return {
            "response": response,
            "employees": [emp.to_dict() for emp in employees]
        }
    else:
        return {"response": f"ℹ️ No employees hired in the last {days} days"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)