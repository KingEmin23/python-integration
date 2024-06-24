import time
import requests
import os
import traceback

from sqlalchemy import create_engine, String, Column, Integer, Boolean, delete
from sqlalchemy.orm import Session, declarative_base
from pickers import *
from dotenv import load_dotenv

load_dotenv()

PG_PASS = os.getenv("PG_PASS")
PG_LOG = os.getenv("PG_LOG")
PG_IP = os.getenv("PG_IP")
PG_PORT = os.getenv("PG_PORT")
PG_DB_NAME = os.getenv("PG_DB_NAME")
OD_TOKEN = os.getenv("OD_TOKEN")
SERV_IP = os.getenv("SERV_IP")
SERV_PORT = int(os.getenv("SERV_PORT"))

try:
    engine = create_engine(f"postgresql+psycopg2://{PG_LOG}:{PG_PASS}@{PG_IP}:{PG_PORT}/{PG_DB_NAME}")
    session = Session(engine)
    base = declarative_base()


    class Ticket(base):
        __tablename__ = "Tickets"
        column_num = Column(Integer, primary_key=True, autoincrement=True, nullable=True)
        is_id = Column(String, nullable=True)
        name = Column(String, nullable=True)
        adr = Column(String, nullable=True)
        date = Column(String, nullable=True)
        team_name = Column(String, nullable=True)
        note_text = Column(String, nullable=True)
        fulfilled = Column(Boolean, default=False, nullable=False)
        added_to_okdesk = Column(Boolean, default=False, nullable=False)
        od_id = Column(String, nullable=True)
        completed_at = Column(String, default=None, nullable=True)
        Solution = Column(String, nullable=True)


    base.metadata.create_all(engine)

except Exception as e:
    traceback_str = traceback.format_exc()
    print(f"ERROR: Creating db exception\n"
          f"{e} \n {traceback_str}")


async def add_to_db(is_id: str, name: str, adr: str, date: str, team_name: str, note_text: str, added_to_okdesk=False,
                    fulfilled=False):
    print("INFO: Adding sorted data to database")
    try:
        with Session(engine) as session:
            session.add(
                Ticket(is_id=is_id, name=name, adr=adr, date=date, team_name=team_name, note_text=note_text,
                       added_to_okdesk=added_to_okdesk, fulfilled=fulfilled))
            session.commit()
            print("INFO: Data added. Session completed")
    except Exception as e:
        traceback_str = traceback.format_exc()
        print("ERROR: Smth went wrong while adding data to database\n"
              f"{e} \n {traceback_str}")


def add_to_od():
    try:
        with Session(engine) as session:
            for i in range(session.query(Ticket).count()):
                temp = session.query(Ticket).filter(Ticket.added_to_okdesk == False).offset(i).first()
                if temp is not None:
                    print("INFO: Creating ticket in OKDESK")
                    sorted_data = {"issue": {"title": temp.team_name, "description": temp.note_text,
                                             "custom_parameters": {"001": temp.adr, "002": temp.date, "006": temp.name,
                                                                   "009": temp.is_id}}}
                    url = f"https://supgen.okdesk.ru/api/v1/issues/?api_token={OD_TOKEN}"
                    res = requests.post(url, json=sorted_data)
                    if res.status_code == 200:
                        temp.added_to_okdesk = True
                        temp.od_id = (res.json()).get("id")
                        session.commit()
                        print(f"INFO: Ticket {temp.od_id} created in OKDESK. Query added.")
                        """функция для изменения статуса инцидента в 4me или же в функции ниже"""

    except Exception as e:
        print(f"ERROR: Smth went wrong when trying to add ticket to OKDESK.\n {e}{traceback.format_exc()}")


def od_status_checker():
    """Функция для проверки статусов инцидентов в ОКДЕКСКЕ через БД"""
    try:
        with Session(engine) as session:
            for i in range(session.query(Ticket).count()):
                temp = session.query(Ticket).filter(Ticket.added_to_okdesk == True and Ticket.od_id != None).offset(
                    i).first()
                if temp:
                    if temp.completed_at is None and temp.Solution is None:
                        res_json = requests.get(
                            f"https://supgen.okdesk.ru/api/v1/issues/{temp.od_id}?api_token={OD_TOKEN}")
                        data = res_json.json()
                        try:
                            status = data["status"]["code"]
                            if status == "Work":
                                """Если берем статус в РАБТЕ, то будем по АПИ менять статус также в 4ME"""
                                pass

                            elif status == "closed":
                                sorted_data = data_picker_for_status_check(res_json.json())
                                temp.completed_at = sorted_data[0]
                                temp.Solution = sorted_data[1]
                                temp.fulfilled = True
                                session.commit()
                                print(f"INFO: Closed ticket info {temp.od_id} added to db")

                            elif status == "completed":
                                sorted_data = data_picker_for_status_check(res_json.json())
                                temp.completed_at = sorted_data[0]
                                temp.Solution = sorted_data[1]
                                temp.fulfilled = True
                                session.commit()
                                print(f"INFO: Completed ticket info {temp.od_id} added to db")
                        except Exception:
                            print(f"ticket {temp.od_id} deleted from data base")
                            session.delete(temp)
                            session.commit()
                            
    except Exception as e:
        print(f"ERROR: Status check in OD and DB exception\n"
              f"er: {e} \n {traceback.format_exc()}")


def finisher():
    """ФУНКЦИЯ ДЛЯ ЗАКРЫТИЯ ИНЦИДЕНТА В 4ME А ТАКЖЕ УДАЛЕНИЯ ИНЦА ИЗ БД НЕ ЗАВЕРШЕНА"""
    try:
        with Session(engine) as session:
            for i in range(session.query(Ticket).count()):
                temp = session.query(Ticket).filter(
                    Ticket.added_to_okdesk != False and Ticket.fulfilled != False).offset(i).first()
                data = {"time": temp.completed_at, "issue": temp.Solution}
                url = "http://127.0.0.1:7001/finalreceiver"
                res = requests.post(url, json=data)
                if res.status_code == 200:
                    session.delete(temp)
                    session.commit()


    except Exception as e:
        print(f"ERROR: {e}")


if __name__ == "__main__":
    while True:
        add_to_od()
        time.sleep(2)
        od_status_checker()
        time.sleep(2)
        # finisher()
