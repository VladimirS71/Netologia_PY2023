# импорты
import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import psycopg2
from config import *



def create_db():
        """
        Заходит под админом и пробует создать базу данных NEPY8 под нужды ORM
        для подключения к вашей базе данных в conn необходимо прописать ВАШИ логин
        и пароль 
        """
        psd = ('password')
        conn = psycopg2.connect(database='NEPY8', user='postgres', password=psd)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        try:
            cur.execute("""CREATE DATABASE NEPY8;""")
            print('[+] База данных NEPY8 создана')
        except Exception as e:
            print(f'[-] База данных NEPY8 была создана ранее')
            conn.rollback()
        conn.close()

class Base(DeclarativeBase): 
    pass

class Viewed(Base):
    __tablename__ = 'users'
    user_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)
    like_id = sq.Column(sq.Boolean(), default=False)
    
    
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

    def add_user(self, user_id: int, worksheet_id: int, like_id: bool=False)-> None:
            self._session.add(Viewed(user_id=user_id, worksheet_id=worksheet_id, like_id=like_id))
            self._session.commit()

    # извлечение записей из БД

    """def check_user(engine, user_id, worksheet_id, like_id: bool=True):
        with Session(engine) as session:
            from_bd = session.query(Viewed).filter(
                Viewed.user_id == user_id,
                Viewed.worksheet_id == worksheet_id,
                Viewed.like_id == like_id
            ).first()
            return from_bd"""

    # обновление записи в бд

    def update_user(self, user_id, worksheet_id, like_id: bool=True)-> None:
            self._session.query(Viewed).filter(Viewed.user_id==user_id, Viewed.worksheet_id==worksheet_id).update({Viewed.like_id: like_id,})
            self._session.commit()


    def viewed_id(self, user_id: int, worksheet_id: int) -> bool:
            bd = self._session.query(Viewed).filter(Viewed.user_id == user_id, Viewed.worksheet_id == worksheet_id).all()
            return True if bd else False
        
    def viewed_favorite(self, user_id: int) -> list:
            self._session.query(Viewed.worksheet_id).filter(Viewed.user_id == user_id, Viewed.like_id == True).all()   
            return
        
if __name__ == '__main__':
    create_db()
    eng = VK_Data_Base()
    #print(eng.request_favorite(user_id=50))
    #eng.add_user(79, 78, True)
    print(eng.viewed_id(user_id=79, worksheet_id=78))
