from src.db.models import User
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.auth.schemas import UserSignupModel
from src.auth.utils import generate_password_hash

class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()
    
    async def is_user_exist(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False
    
    async def create_user(self, user_data: UserSignupModel, session: AsyncSession):
        user_data_dic = user_data.model_dump()
        new_user = User(**user_data_dic)
        new_user.password_hash = generate_password_hash(user_data_dic["password"])
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        return new_user
    
    async def update_user(self, user: User, updated_data: dict, session: AsyncSession):
        for key, value in updated_data.items():
            setattr(user, key, value)
        await session.commit()
        return user
