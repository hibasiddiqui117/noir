from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from .models import Employee
from .schemas import EmployeeCreate, EmployeeUpdate

def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    """Get employee by ID"""
    return db.query(Employee).filter(Employee.id == employee_id).first()

def get_employee_by_emp_id(db: Session, emp_id: str) -> Optional[Employee]:
    """Get employee by employee ID"""
    return db.query(Employee).filter(Employee.employee_id == emp_id).first()

def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    """Get employee by email"""
    return db.query(Employee).filter(Employee.email == email).first()

def get_employees(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False
) -> List[Employee]:
    """Get employees with filtering and sorting"""
    query = db.query(Employee)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.department.ilike(search_term),
                Employee.position.ilike(search_term),
                Employee.employee_id.ilike(search_term),
                Employee.email.ilike(search_term)
            )
        )
    
    if department:
        query = query.filter(Employee.department == department)
    
    if status:
        query = query.filter(Employee.status == status)
    
    if sort_by:
        sort_column = getattr(Employee, sort_by, None)
        if sort_column:
            if sort_desc:
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
    
    return query.offset(skip).limit(limit).all()

def get_employee_count(
    db: Session,
    search: Optional[str] = None,
    department: Optional[str] = None,
    status: Optional[str] = None
) -> int:
    """Get total count of employees with filters"""
    query = db.query(Employee)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Employee.first_name.ilike(search_term),
                Employee.last_name.ilike(search_term),
                Employee.department.ilike(search_term),
                Employee.position.ilike(search_term),
                Employee.employee_id.ilike(search_term),
                Employee.email.ilike(search_term)
            )
        )
    
    if department:
        query = query.filter(Employee.department == department)
    
    if status:
        query = query.filter(Employee.status == status)
    
    return query.count()

def create_employee(db: Session, employee: EmployeeCreate) -> Employee:
    """Create a new employee"""
    db_employee = Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def update_employee(db: Session, employee_id: int, employee_update: EmployeeUpdate) -> Optional[Employee]:
    """Update an employee - only updates fields that are provided"""
    db_employee = get_employee(db, employee_id)
    if db_employee:
        # Get only the fields that were provided (not None)
        update_data = employee_update.dict(exclude_unset=True)
        
        # Update only the fields that were provided
        for key, value in update_data.items():
            if value is not None:  # Only update if value is not None
                setattr(db_employee, key, value)
        
        # Update the updated_at timestamp
        db_employee.updated_at = datetime.now()
        
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int) -> bool:
    """Delete an employee"""
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False

def get_department_stats(db: Session) -> List[Dict[str, Any]]:
    """Get statistics by department"""
    results = db.query(
        Employee.department,
        func.count(Employee.id).label('count'),
        func.avg(Employee.salary).label('avg_salary'),
        func.min(Employee.salary).label('min_salary'),
        func.max(Employee.salary).label('max_salary')
    ).group_by(Employee.department).all()
    
    return [
        {
            "department": r.department,
            "count": r.count,
            "avg_salary": round(r.avg_salary, 2) if r.avg_salary else 0,
            "min_salary": round(r.min_salary, 2) if r.min_salary else 0,
            "max_salary": round(r.max_salary, 2) if r.max_salary else 0
        }
        for r in results
    ]

def get_overall_stats(db: Session) -> Dict[str, Any]:
    """Get overall employee statistics"""
    total = db.query(Employee).count()
    active = db.query(Employee).filter(Employee.status == 'Active').count()
    avg_salary = db.query(func.avg(Employee.salary)).scalar() or 0
    
    return {
        "total_employees": total,
        "active_employees": active,
        "inactive_employees": total - active,
        "avg_salary_overall": round(avg_salary, 2),
        "departments": get_department_stats(db)
    }

def get_employees_by_department(db: Session, department: str) -> List[Employee]:
    """Get all employees in a department"""
    return db.query(Employee).filter(Employee.department == department).all()

def get_recent_hires(db: Session, days: int = 30) -> List[Employee]:
    """Get employees hired in the last N days"""
    cutoff_date = datetime.now().date() - timedelta(days=days)
    return db.query(Employee).filter(Employee.hire_date >= cutoff_date).all()

def search_employees(db: Session, query: str) -> List[Employee]:
    """Search employees by name, department, or position"""
    search_term = f"%{query}%"
    return db.query(Employee).filter(
        or_(
            Employee.first_name.ilike(search_term),
            Employee.last_name.ilike(search_term),
            Employee.department.ilike(search_term),
            Employee.position.ilike(search_term)
        )
    ).all()

def to_employee_response(employee: Employee) -> dict:
    """Helper function to convert Employee model to response dict"""
    return {
        "id": employee.id,
        "employee_id": employee.employee_id,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "full_name": f"{employee.first_name} {employee.last_name}",
        "email": employee.email,
        "department": employee.department,
        "position": employee.position,
        "salary": employee.salary,
        "hire_date": employee.hire_date,
        "status": employee.status
    }