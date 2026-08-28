from sqlalchemy import Column, Integer, String, Float, Date, DateTime
from sqlalchemy.sql import func
from .database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(20), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    department = Column(String(50), nullable=False, index=True)
    position = Column(String(50), nullable=False)
    salary = Column(Float, nullable=False)
    hire_date = Column(Date, nullable=False)
    status = Column(String(20), default='Active', index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add this property to generate full_name
    @property
    def full_name(self):
        """Return the full name of the employee"""
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Employee {self.employee_id}: {self.first_name} {self.last_name}>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "department": self.department,
            "position": self.position,
            "salary": self.salary,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "status": self.status,
            "full_name": self.full_name,  # Now this will work
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }