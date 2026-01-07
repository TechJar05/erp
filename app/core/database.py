from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "postgresql://erp_db:ykTG9r4mc2wCLURiiLNC353UebNed7sb@dpg-d5eutjq4d50c73cclr9g-a.singapore-postgres.render.com/erp_db_e1qo"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()
