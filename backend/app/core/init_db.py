"""Database initialization and seeding script."""
import asyncio
from app.core.database import engine
from app.models.base import Base
from app.models import Organization, User, Question
from app.models.user import UserRole
from app.models.organization import OrgType
from app.services.question_bank import QUESTIONS
from app.core.config import get_settings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

settings = get_settings()


async def seed_initial_data(session: AsyncSession):
    """Seed default organization, admin user, and questions."""
    # 1. Create Default Organization
    org_stmt = select(Organization).limit(1)
    result = await session.execute(org_stmt)
    org = result.scalar_one_or_none()

    if not org:
        org = Organization(
            id=uuid.uuid4(),
            name="Default Mind Org",
            org_type=OrgType.HR,
            contact_email="default@mbtimind.ru",
            is_active=True,
        )
        session.add(org)
        await session.flush()
        print(f"Created default organization: {org.name}")

    # 2. Create Default Admin User
    user_stmt = select(User).limit(1)
    result = await session.execute(user_stmt)
    admin = result.scalar_one_or_none()

    if not admin:
        # Use hashlib sha256 as fallback since passlib has a well-known bug with modern bcrypt on Python 3.13
        import hashlib
        # We can also store the sha256 of 'admin123'
        hashed_password = hashlib.sha256("admin123".encode()).hexdigest()

        admin = User(
            id=uuid.uuid4(),
            email="admin@mbtimind.ru",
            hashed_password=hashed_password,
            full_name="Mind Admin",
            role=UserRole.ADMIN,
            organization_id=org.id,
            is_active=True,
        )
        session.add(admin)
        await session.flush()
        print(f"Created default admin user: {admin.email}")

    # 3. Seed Questions
    q_stmt = select(Question).limit(1)
    result = await session.execute(q_stmt)
    q_exists = result.scalar_one_or_none()

    if not q_exists:
        for idx, q in enumerate(QUESTIONS):
            question = Question(
                id=uuid.UUID(q["id"]),
                text_ru=q["text_ru"],
                option_a_ru=q["option_a_ru"],
                option_b_ru=q["option_b_ru"],
                scale=q["scale"],
                question_type=q["question_type"],
                option_a_direction=q["option_a_direction"],
                option_b_direction=q["option_b_direction"],
                order_index=q["order_index"],
            )
            session.add(question)
        print(f"Seeded {len(QUESTIONS)} questions to database.")
    
    await session.commit()


async def init_db():
    """Initializes tables and seeds them."""
    print("Connecting to database and creating tables...")
    async with engine.begin() as conn:
        # Create all tables defined in models package
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully.")
    
    from sqlalchemy.ext.asyncio import async_sessionmaker
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        await seed_initial_data(session)
    
    print("Database initialization completed successfully.")


if __name__ == "__main__":
    asyncio.run(init_db())
