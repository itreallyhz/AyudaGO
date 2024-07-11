from sqlalchemy import Column, Integer, String, Date, ForeignKey, LargeBinary, Time, DECIMAL, CHAR
from sqlalchemy.orm import sessionmaker, relationship
from database import Base
from sqlalchemy import create_engine
from sqlalchemy.event import listens_for
from sqlalchemy import text

class User(Base):
    __tablename__ = 'users'
    user_ID = Column(CHAR(15), primary_key=True, default='2023-00000-NC')
    user_email = Column(String(50), nullable=False, unique=True)
    user_password = Column(String(255), nullable=True, default=None)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    last_name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)
    house_no = Column(String(50))
    street = Column(String(50), nullable=False)
    vill_subd = Column(String(50), nullable=False)
    brgy = Column(String(50), nullable=False, default='Brgy. 171')
    city = Column(String(50), nullable=False, default='Caloocan City')
    valid_ID = Column(LargeBinary, nullable=False)
    phone_num = Column(String(50), nullable=False)
    ewallet = Column(String(50), nullable=False)
    acc_status = Column(String(50), nullable=False, default='pending')
    otp = Column(String(255), nullable=True, default=None)
    fund_entries = relationship("FundEntry", back_populates="user")

    def __repr__(self):
        return '<User %r>' % (self.user_ID)

    
# Admin models/schemas
class Admin(Base):
    __tablename__ = 'admins'
    admin_ID = Column(Integer, primary_key=True)
    admin_email = Column(String(50), nullable=False, unique=True)
    admin_password = Column(String(50), nullable=False)
  
 
    def __repr__(self):
        return '<Admin %r>' % (self.admin_ID)

class FundEntry(Base):
    __tablename__ = 'fund_entry'
    fund_ID = Column(Integer, primary_key=True)
    fund_date = Column(Date)  
    fund_amount = Column(DECIMAL)
    fund_status = Column(String(50), nullable=True)
    user_ID = Column(CHAR(15), ForeignKey('users.user_ID'))  # Update the column name
    user = relationship("User", back_populates="fund_entries")

    def __repr__(self):
        return '<FundEntry %r>' % (self.fund_ID)


# Announcement models/schemas
class Announcement(Base):
    __tablename__ = 'announcements'
    a_ID = Column(Integer, primary_key=True)
    a_title = Column(String(50))
    a_date = Column(Date)
    a_time = Column(Time)
    a_location = Column(String(50))
    a_description = Column(String(1000))

    def __repr__(self):
        return '<Announcement %r>' % (self.a_ID)


DB_URL = f'mysql+pymysql://root:D%40t%40b%40s3@localhost:3306/agdb1'

engine = create_engine(DB_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

try:
    # create queries to retrieve the unique values for each dropdown menu
    street_results = session.query(
        User.street).distinct().order_by(User.street).all()
    barangay_results = session.query(
        User.brgy).distinct().order_by(User.brgy).all()
    city_results = session.query(
        User.city).distinct().order_by(User.city).all()

    # create a list of tuples from the query results
    street_options = [(row[0], row[0]) for row in street_results]
    barangay_options = [(row[0], row[0]) for row in barangay_results]
    city_options = [(row[0], row[0]) for row in city_results]

finally:
    # close the session to release resources
    session.close()

    # Event listener to generate auto-incremented user_ID
@listens_for(User, 'before_insert')
def generate_user_ID(mapper, connection, target):
    # Query the maximum user_ID to determine the next number
    max_user_id = connection.scalar(text("SELECT MAX(user_ID) FROM users"))
    if max_user_id:
        next_number = int(max_user_id.split('-')[1]) + 1
    else:
        next_number = 1

    # Generate the new user_ID
    target.user_ID = f'2023-{str(next_number).zfill(5)}-NC'
