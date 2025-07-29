from sqlalchemy.orm import Session
import models, schemas

def get_user_by_email(db: Session, email: str):
    """Fetches a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_or_update_user_profile(db: Session, user_data: schemas.UserCreate):
    """
    Creates a new user and profile, or updates the profile for an existing user.
    This logic is now more robust to handle all cases correctly.
    """
    # Check if the user already exists in the database
    db_user = get_user_by_email(db, email=user_data.email)

    # Get the detailed financial data from the request payload
    p_data = user_data.profile_data

    if db_user:
        # --- USER EXISTS ---
        # Get their existing financial profile
        profile = db_user.financial_profile
        # Data integrity check: if a user somehow exists without a profile, create one.
        if not profile:
            profile = models.FinancialProfile(user_id=db_user.id)
            db.add(profile)
    else:
        # --- USER DOES NOT EXIST ---
        # Create a new user object
        db_user = models.User(email=user_data.email)
        db.add(db_user)
        # Flush the session to assign an ID to the new user before creating the profile
        db.flush()
        # Create a new financial profile linked to the new user's ID
        profile = models.FinancialProfile(user_id=db_user.id)
        db.add(profile)

    # --- UPDATE PROFILE ---
    # Now, update the profile object (whether new or existing) with all the data
    
    # Profile Info
    profile.age_group = p_data.profile.age_group
    profile.resident_status = p_data.profile.resident_status
    
    # Income Details
    profile.salary_total = p_data.income.salary.salary_total
    profile.salary_basic = p_data.income.salary.salary_basic
    profile.salary_hra = p_data.income.salary.salary_hra
    profile.hp_rent_received = p_data.income.house_property.hp_rent_received
    profile.hp_municipal_taxes = p_data.income.house_property.hp_municipal_taxes
    profile.capital_gains = p_data.income.capital_gains
    profile.business_profession = p_data.income.business_profession
    profile.other_sources = p_data.income.other_sources
    profile.other_sources_interest_savings = p_data.income.other_sources_interest_savings
    
    # Deductions Details
    profile.rent_paid = p_data.deductions.hra_details.rent_paid
    profile.is_metro = p_data.deductions.hra_details.is_metro
    profile.section_80c = p_data.deductions.section_80c
    profile.section_80ccd_1b = p_data.deductions.section_80ccd_1b
    profile.section_80d_self = p_data.deductions.section_80d_self
    profile.self_above_60 = p_data.deductions.self_above_60
    profile.section_80d_parents = p_data.deductions.section_80d_parents
    profile.parents_above_60 = p_data.deductions.parents_above_60
    profile.section_24b = p_data.deductions.section_24b
    profile.section_80e = p_data.deductions.section_80e
    profile.section_80g = p_data.deductions.section_80g
    profile.section_80u = p_data.deductions.section_80u
    profile.section_80dd = p_data.deductions.section_80dd

    # Commit all the changes (new user/profile and/or updates) to the database
    db.commit()
    # Refresh the user object to get the latest state from the database
    db.refresh(db_user)
    
    return db_user
