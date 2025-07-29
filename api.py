from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud, models, schemas, predict
from database import SessionLocal, engine

# Create all database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI(title="AI Tax Advisor API")

# Configure CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, you can restrict this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# --- Dependency Injection for Database Session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@app.post("/profile", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_or_update_profile(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create or update a user profile with financial data.
    """
    try:
        return crud.create_or_update_user_profile(db=db, user_data=user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while saving the profile: {e}"
        )

@app.get("/profile/{email}", response_model=schemas.FinancialProfileBase)
def get_profile(email: str, db: Session = Depends(get_db)):
    """
    Retrieve an existing user's financial profile by email.
    """
    user = crud.get_user_by_email(db, email=email)
    if not user or not user.financial_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found for this email."
        )

    p = user.financial_profile
    return schemas.FinancialProfileBase(
        profile=schemas.Profile(
            age_group=p.age_group,
            resident_status=p.resident_status
        ),
        income=schemas.Income(
            salary=schemas.SalaryIncome(
                salary_total=p.salary_total,
                salary_basic=p.salary_basic,
                salary_hra=p.salary_hra
            ),
            house_property=schemas.HousePropertyIncome(
                hp_rent_received=p.hp_rent_received,
                hp_municipal_taxes=p.hp_municipal_taxes
            ),
            capital_gains=p.capital_gains,
            business_profession=p.business_profession,
            other_sources=p.other_sources,
            other_sources_interest_savings=p.other_sources_interest_savings
        ),
        deductions=schemas.Deductions(
            hra_details=schemas.HraDeduction(
                rent_paid=p.rent_paid,
                is_metro=p.is_metro
            ),
            section_80c=p.section_80c,
            section_80ccd_1b=p.section_80ccd_1b,
            section_80d_self=p.section_80d_self,
            self_above_60=p.self_above_60,
            section_80d_parents=p.section_80d_parents,
            parents_above_60=p.parents_above_60,
            section_24b=p.section_24b,
            section_80e=p.section_80e,
            section_80g=p.section_80g,
            section_80u=p.section_80u,
            section_80dd=p.section_80dd
        )
    )

@app.post("/calculate/{email}")
def calculate_for_user(email: str, db: Session = Depends(get_db)):
    """
    Run the tax calculation for a user with a saved profile.
    """
    user = crud.get_user_by_email(db, email=email)
    if not user or not user.financial_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please save a profile before calculating."
        )

    p = user.financial_profile

    # Convert SQLAlchemy model to dictionary for prediction function
    profile_dict = { "age_group": p.age_group, "resident_status": p.resident_status }
    income_dict = {
        "salary": { "salary_total": p.salary_total, "salary_basic": p.salary_basic, "salary_hra": p.salary_hra },
        "house_property": { "hp_rent_received": p.hp_rent_received, "hp_municipal_taxes": p.hp_municipal_taxes },
        "capital_gains": p.capital_gains, "business_profession": p.business_profession,
        "other_sources": p.other_sources, "other_sources_interest_savings": p.other_sources_interest_savings
    }
    deductions_dict = {
        "hra_details": { "rent_paid": p.rent_paid, "is_metro": p.is_metro },
        "section_80c": p.section_80c, "section_80ccd_1b": p.section_80ccd_1b,
        "section_80d_self": p.section_80d_self, "self_above_60": p.self_above_60,
        "section_80d_parents": p.section_80d_parents, "parents_above_60": p.parents_above_60,
        "section_24b": p.section_24b, "section_80e": p.section_80e, "section_80g": p.section_80g,
        "section_80u": p.section_80u, "section_80dd": p.section_80dd
    }

    try:
        return predict.run_prediction(profile=profile_dict, income=income_dict, deductions=deductions_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during tax calculation: {e}"
        )

@app.get("/")
def read_root():
    return {"status": "AI Tax Advisor API is running"}
