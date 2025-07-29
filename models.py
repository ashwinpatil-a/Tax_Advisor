from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    # One-to-one relationship with FinancialProfile
    # Cascade deletes the associated profile when user is deleted
    financial_profile = relationship(
        "FinancialProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )


class FinancialProfile(Base):
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # --- Profile Info ---
    age_group = Column(String, default='below_60')
    resident_status = Column(String, default='resident')

    # --- Income Fields ---
    salary_total = Column(Float, default=0)
    salary_basic = Column(Float, default=0)
    salary_hra = Column(Float, default=0)
    hp_rent_received = Column(Float, default=0)
    hp_municipal_taxes = Column(Float, default=0)
    capital_gains = Column(Float, default=0)
    business_profession = Column(Float, default=0)
    other_sources = Column(Float, default=0)
    other_sources_interest_savings = Column(Float, default=0)

    # --- Deduction Fields ---
    rent_paid = Column(Float, default=0)
    is_metro = Column(Boolean, default=False)

    section_80c = Column(Float, default=0)
    section_80ccd_1b = Column(Float, default=0)
    section_80d_self = Column(Float, default=0)
    self_above_60 = Column(Boolean, default=False)
    section_80d_parents = Column(Float, default=0)
    parents_above_60 = Column(Boolean, default=False)
    section_24b = Column(Float, default=0)
    section_80e = Column(Float, default=0)
    section_80g = Column(Float, default=0)
    section_80u = Column(String, default='none')      # values: none / disability / severe_disability
    section_80dd = Column(String, default='none')     # values: none / disability / severe_disability

    # Link back to User
    user = relationship("User", back_populates="financial_profile")
