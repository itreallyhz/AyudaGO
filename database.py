from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
 
DB_USER = 'root'
DB_PASSWORD = 'D%40t%40b%40s3'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME ='agdb1'

DB_URL = f'mysql+pymysql://root:D%40t%40b%40s3@localhost:3306/agdb1'
 
engine = create_engine(DB_URL)
sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()