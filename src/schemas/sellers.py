from typing import List
from src.schemas import ReturnedBook
from pydantic import BaseModel, Field

__all__ = ["IncomingSeller", "ReturnedSeller", "ReturnedAllSellers", "NewSeller"]


# Базовый класс "Продавцы", содержащий поля, которые есть во всех классах-наследниках.
class BaseSeller(BaseModel):
    first_name: str
    last_name: str
    e_mail: str


# Класс для валидации входящих данных. Не содержит id так как его присваивает БД.
class IncomingSeller(BaseSeller):
    password: str = Field(
        min_length=8
    )  

    
# Класс для создания нового продавца. Не пытается вытянуть из базы данные по книгам, 
# в отличие от Returned
class NewSeller(BaseSeller):
    id: int 



# Класс, валидирующий исходящие данные. Он уже содержит id и books
class ReturnedSeller(BaseSeller):
    id: int
    books: List[ReturnedBook]

    class Config:
        from_attributes = True #чтоб ORM доставала данные о books
        

# Класс для возврата массива объектов "Продавец"
class ReturnedAllSellers(BaseModel):
    sellers: list[NewSeller]

   
