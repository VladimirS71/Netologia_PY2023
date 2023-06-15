# импорты
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import db_url_object

class Base(DeclarativeBase): 
    pass

class Viewed(Base):
    __tablename__ = 'users'
    user_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)
    favourites = sq.Column(sq.Boolean(), default=False)
    
    
class VK_Data_Base:

    def __init__(self):
        self._engine = self._create_engine_connection()
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        self._create_tables()

    def _create_engine_connection(self):
        """Создаёт движок сессии"""
        DSN = db_url_object 
        engine = sq.create_engine(DSN)
        return engine

    def _create_tables(self):
        # Base.metadata.drop_all(bind=self._engine)
        Base.metadata.create_all(self._engine)
    
       
    # добавление записи в бд

    def add_user(self, user_id: int, worksheet_id: int, favourites: bool=False)-> None:
            self._session.add(Viewed(user_id=user_id, worksheet_id=worksheet_id, favourites=favourites))
            self._session.commit()

    # обновление записи в бд

    def update_user(self, user_id, worksheet_id, favourites: bool=True)-> None:
            self._session.query(Viewed).filter(Viewed.user_id==user_id, Viewed.worksheet_id==worksheet_id).update({Viewed.favourites: favourites})
            self._session.commit()

    # проверка наличия записи в бд 

    def viewed_id(self, user_id: int, worksheet_id: int) -> bool:
            bd = self._session.query(Viewed).filter(Viewed.user_id == user_id, Viewed.worksheet_id == worksheet_id).all()
            return True if bd else False
    
    # список анкет в избранном 

    def viewed_favorite(self, user_id: int) -> list:
            list = self._session.query(Viewed.worksheet_id).filter(Viewed.user_id == user_id, Viewed.favourites == True).all()   
            return list
        
if __name__ == '__main__':
    eng = VK_Data_Base()
    print(eng.viewed_favorite(user_id=''))
