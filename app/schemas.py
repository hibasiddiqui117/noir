from pydantic import BaseModel, EmailStr, Field, validator, computed_field
from datetime import date, datetime
from typing import Optional, List

class EmployeeBase(BaseModel):
    """Base employee schema"""
    employee_id: str = Field(..., min_length=3, max_length=20)
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    department: str = Field(..., min_length=2, max_length=50)
    position: str = Field(..., min_length=2, max_length=50)
    salary: float = Field(..., gt=0, le=1000000)
    hire_date: date
    status: Optional[str] = "Active"
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if not v.startswith('EMP'):
            raise ValueError('Employee ID must start with "EMP"')
        return v

class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee"""
    pass

class EmployeeUpdate(BaseModel):
    """Schema for updating an employee - ALL FIELDS OPTIONAL"""
    employee_id: Optional[str] = Field(None, min_length=3, max_length=20)
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    department: Optional[str] = Field(None, min_length=2, max_length=50)
    position: Optional[str] = Field(None, min_length=2, max_length=50)
    salary: Optional[float] = Field(None, gt=0, le=1000000)
    hire_date: Optional[date] = None
    status: Optional[str] = Field(None, pattern="^(Active|Inactive)$")
    
    @validator('employee_id')
    def validate_employee_id(cls, v):
        if v and not v.startswith('EMP'):
            raise ValueError('Employee ID must start with "EMP"')
        return v

class EmployeeResponse(EmployeeBase):
    """Schema for returning employee data"""
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @computed_field
    @property
    def full_name(self) -> str:
        """Generate full name from first and last name"""
        return f"{self.first_name} {self.last_name}"
    
    class Config:
        from_attributes = True

class EmployeeListResponse(BaseModel):
    """Schema for paginated employee list"""
    total: int
    employees: List[EmployeeResponse]

class DepartmentStats(BaseModel):
    """Schema for department statistics"""
    department: str
    count: int
    avg_salary: float
    min_salary: float
    max_salary: float

class EmployeeStats(BaseModel):
    """Schema for overall employee statistics"""
    total_employees: int
    active_employees: int
    inactive_employees: int
    avg_salary_overall: float
    departments: List[DepartmentStats]