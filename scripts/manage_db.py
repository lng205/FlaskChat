"""
This is a helper script to manage the database.
"""

from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import *
engine = create_engine("sqlite:///database/main.db", echo=False)

def main():
    clear_messages(1)

def clear_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

def clear_messages(room_id):
    with Session(engine) as session:
        session.execute(delete(Message).where(Message.room_id == room_id))

if __name__ == "__main__":
    main()