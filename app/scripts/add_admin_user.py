import asyncio
from app.db.session import get_session
from app.db.models import User
from app.core.security import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession

async def add_admin_user():
    # Get the session
    async for session in get_session():  # Use async for to get session from the generator
        # Create an admin user
        hashed_password = get_password_hash("admin_password")
        admin_user = User(email="admin@example.com", hashed_password=hashed_password, is_admin=True)

        # Add user to session and commit
        session.add(admin_user)
        await session.commit()
        print(f"Admin user {admin_user.email} added successfully.")

# Run the script
asyncio.run(add_admin_user())
