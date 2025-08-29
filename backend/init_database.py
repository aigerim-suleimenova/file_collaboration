#!/usr/bin/env python3
"""
Initialize the database and create the first superuser.
"""
from sqlmodel import SQLModel, create_engine, Session, select
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import User, UserCreate


def main():
    # Create database engine
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

    # Create all tables
    SQLModel.metadata.create_all(engine)

    # Initialize database with superuser
    with Session(engine) as session:
        # Check if superuser already exists
        existing_user = session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()

        if not existing_user:
            # Create superuser
            superuser = User(
                email=settings.FIRST_SUPERUSER,
                hashed_password=get_password_hash(
                    settings.FIRST_SUPERUSER_PASSWORD),
                full_name="Admin User",
                is_active=True,
                is_superuser=True,
            )
            session.add(superuser)
            session.commit()
            print("✅ Database initialized successfully!")
            print(f"✅ Superuser created: {settings.FIRST_SUPERUSER}")
        else:
            print("✅ Database already initialized!")
            print(f"✅ Superuser already exists: {settings.FIRST_SUPERUSER}")


if __name__ == "__main__":
    main()
