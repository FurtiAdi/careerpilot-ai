from fastapi import (
    Depends,
    HTTPException
)

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.models.user_model import User

from app.services.auth_service import (
    verify_token
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login",
    auto_error=False,
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication token is required.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )
    
    email = verify_token(token)

    if not email:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )               

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return user