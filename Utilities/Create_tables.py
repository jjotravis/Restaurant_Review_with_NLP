#!/usr/bin/env python3
from Db import engine, Base

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
