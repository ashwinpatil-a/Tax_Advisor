from pydantic import BaseModel, EmailStr
from typing import List

# --- Sub-models for nested data structures ---

class Profile(BaseModel):
    age_group: str
    resident_status: str

class SalaryIncome(BaseModel):
    salary_total: float
    salary_basic: float
    salary_hra: float

class HousePropertyIncome(BaseModel):
    hp_rent_received: float
    hp_municipal_taxes: float

class Income(BaseModel):
    salary: SalaryIncome
    house_property: HousePropertyIncome
    capital_gains: float
    business_profession: float
    other_sources: float
    other_sources_interest_savings: float

class HraDeduction(BaseModel):
    rent_paid: float
    is_metro: bool

class Deductions(BaseModel):
    hra_details: HraDeduction
    section_80c: float
    section_80ccd_1b: float
    section_80d_self: float
    self_above_60: bool
    section_80d_parents: float
    parents_above_60: bool
    section_24b: float
    section_80e: float
    section_80g: float
    section_80u: str
    section_80dd: str

# --- Main models for API requests and responses ---

class FinancialProfileBase(BaseModel):
    """The core model representing all financial data."""
    profile: Profile
    income: Income
    deductions: Deductions

class UserCreate(BaseModel):
    """Model for creating/updating a user profile via the API."""
    email: EmailStr
    profile_data: FinancialProfileBase

class User(BaseModel):
    """Model for reading a user from the database."""
    id: int
    email: EmailStr
    
    class Config:
        from_attributes = True # Replaces orm_mode = True
