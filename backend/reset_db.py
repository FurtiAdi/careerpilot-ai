from app.database.database import Base, engine

from app.models.analysis_model import Analysis
from app.models.user_model import User

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Database reset complete!")