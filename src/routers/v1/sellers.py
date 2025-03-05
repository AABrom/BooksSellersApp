from typing import Annotated
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from src.models.sellers import Seller
from src.models.books import Book
from src.schemas import IncomingSeller, ReturnedSeller, ReturnedAllSellers, NewSeller
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession
from src.configurations import get_async_session

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")


DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Ручка для создания записи о продавце в БД. Возвращает созданного продавца.
@sellers_router.post(
    "/", response_model=NewSeller, status_code=status.HTTP_201_CREATED
)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller,
    session: DBSession,
):  # прописываем модель валидирующую входные данные
    # session = get_async_session() вместо этого мы используем иньекцию зависимостей DBSession

    # это - бизнес логика. Обрабатываем данные, сохраняем, преобразуем и т.д.
    new_seller = Seller(
        **{

            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "e_mail": seller.e_mail,
            "password": seller.password,
        }
    )

    session.add(new_seller)
    await session.flush()

    return new_seller


# Ручка, возвращающая всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers, )
async def get_all_sellers(session: DBSession):
    
    query = select(Seller.id, Seller.first_name, Seller.last_name, Seller.e_mail)

    # Выполняем запрос
    results = await session.execute(query)
    sellers = results.all()  

    #извлекаем по отдельности только нужные поля
    sellers_list = [
        {"id": seller.id,
         "first_name": seller.first_name,
         "last_name": seller.last_name,
         "e_mail": seller.e_mail}
        for seller in sellers
    ]
    
   
    return {'sellers': sellers_list}
   


# Ручка для получения продавца по его ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    # Используем selectinload для загрузки книг, иначе сыпет MissingGreenlet
    query = select(Seller).where(Seller.id == seller_id).options(selectinload(Seller.books))
    result = await session.execute(query)
    seller = result.scalars().first()

    if not seller:
        return Response(status_code=status.HTTP_404_NOT_FOUND)

    return seller
    


# Ручка для удаления продавца c книгами (см параметр в relationships)
@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    
    if deleted_seller:
        await session.delete(deleted_seller)
    else:
        return Response(status_code=status.HTTP_404_NOT_FOUND)


# Ручка для обновления данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, new_seller_data: ReturnedSeller, session: DBSession):
   
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_seller_data.first_name
        updated_seller.last_name = new_seller_data.last_name
        updated_seller.e_mail = new_seller_data.e_mail

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
