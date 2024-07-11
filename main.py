from fastapi import FastAPI, Request, Depends, Form, status, File, HTTPException, Header, Query
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, sessionmaker
from passlib.hash import bcrypt
from urllib.parse import urlencode
import plotly.graph_objects as go

from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.declarative import declarative_base

from datetime import date, time, datetime, timedelta
from decimal import Decimal
import hashlib

from typing import Optional
import bcrypt
import models
from models import User, Admin, FundEntry

from database import engine, sessionlocal

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

class TokenData(BaseModel):
    email: str
    
# JWT authentication settings
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency to get the database session
def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Verify password
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Get user by email
def get_user_by_email(db, email: str):
    return db.query(User).filter_by(user_email=email).first()

# Authenticate user
def authenticate_user(db, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.user_password):
        return False
    return user

# Create access token
def create_access_token(data: dict, expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = TokenData(email=email)
    except (JWTError, ValidationError):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = get_user_by_email(db, token_data.email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# Get current active user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    user = get_user_by_email(db, token_data.email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

#decode and verify the access token 
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# Login and issue access token
# @app.post("/token")
# async def login_for_access_token(
#     form_data: OAuth2PasswordRequestForm = Depends(),
#     db=Depends(get_db)
# ):
#     user = authenticate_user(db, form_data.username, form_data.password)
#     if not user:
#         raise HTTPException(
#             status_code=401,
#             detail="Incorrect email or password",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     access_token = create_access_token(data={"sub": user.user_email}, expires_delta=access_token_expires)




#     return {"access_token": access_token, "token_type": "bearer"}

# Protected route
@app.get("/users/me/")
async def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        token_data = TokenData(email=email)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    user = get_user_by_email(db, token_data.email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user



#index.html----------------------------------------------------------------------------------------------------------------
@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    announcements = db.query(models.Announcement).\
    order_by(models.Announcement.a_ID.desc()).\
    first()
    return templates.TemplateResponse("index.html", {"request": request, "announcements": [announcements]})

# GENERAL USER==============================================================================================================
@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if user:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user.user_email}, expires_delta=access_token_expires)
        # return {"access_token": access_token, "token_type": "bearer"}
        redirect_url = "/userhome"
        query_params = {"access_token": access_token}

        # Append query parameters to the redirect URL
        if query_params:
            encoded_params = urlencode(query_params)
            redirect_url = f"{redirect_url}?{encoded_params}"
    
        # Create the RedirectResponse and set the Authorization header
        response = RedirectResponse(url=redirect_url)
        response.headers["Authorization"] = f"Bearer {access_token}"

        return response

    admin = db.query(Admin).filter_by(admin_email=username).first()
    if admin and admin.admin_password == password:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": admin.admin_email}, expires_delta=access_token_expires)
        # return {"access_token": access_token, "token_type": "bearer"} 
        redirect_url = "/dashboard1"
        query_params = {"access_token": access_token}
        
        # Append query parameters to the redirect URL
        if query_params:
            encoded_params = urlencode(query_params)
            redirect_url = f"{redirect_url}?{encoded_params}"
    
        # Create the RedirectResponse and set the Authorization header
        response = RedirectResponse(url=redirect_url)
        response.headers["Authorization"] = f"Bearer {access_token}"

        return response

    # Return an error message as a pop-up
    message = "Incorrect username or password"
    return HTMLResponse(content=f"<script>alert('{message}'); window.location='/'</script>", status_code=401)
    
# link to register.html
@app.get("/reg")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

#register
@app.post("/add")
async def add(request: Request,
              first_name: str = Form(...),
              middle_name: str = Form(...),
              last_name: str = Form(...),
              birth_date: date = Form(...),
              house_no: str = Form(...),
              street: str = Form(...),
              vill_subd: Optional[str] = Form(None),
              valid_ID: bytes= File(...),
              phone_num: int = Form(...),
              user_email: str = Form(...),
              ewallet: int = Form(...),
              acc_status: str = Form(...),
              db: Session = Depends(get_db)
              ):
    print(first_name)
    print(middle_name)
    print(last_name)
    print(birth_date)
    print(house_no)
    print(street)
    print(vill_subd)
    print(valid_ID)
    print(phone_num)
    print(user_email)
    print(ewallet)
    print(acc_status)
    
    users = models.User(first_name=first_name,
                        middle_name=middle_name,
                        last_name=last_name,
                        birth_date=birth_date,
                        house_no = house_no,
                        street=street,
                        vill_subd=vill_subd,
                        valid_ID=valid_ID,
                        phone_num=phone_num,
                        user_email=user_email,
                        ewallet=ewallet,
                        acc_status=acc_status,)
    db.add(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("register2"), status_code=status.HTTP_303_SEE_OTHER)

# link to register2.html
@app.get("/register2")
async def register2(request: Request):
    return templates.TemplateResponse("reg2.html", {"request": request})

# link to forgotpassword.html
@app.get("/forgotpassword")
async def forgotpassword(request: Request):
    return templates.TemplateResponse("forgotpassword.html", {"request": request})

# link to changepass.html
@app.get("/changepass")
async def changepass(request: Request):
    return templates.TemplateResponse("changepass.html", {"request": request})

# link to otp.html-------------------------------------------------------------------------------------------------------------------
@app.get("/code/{email}/{otp}")
async def code(email: str, otp: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_email == email).first()
    if user:
        # Hash the OTP code
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()

        # Save the hashed OTP code in the user's record
        user.otp = otp_hash
        db.commit()
        return RedirectResponse(url="/otp")  # Redirect to the otp page
    else:
        message = "Email is unique. It can't be Repeated."
        return HTMLResponse(content=f"<script>alert('{message}'); window.location='/confirmpass'</script>", status_code=401)
@app.get("/otp")
async def otp(request: Request):
    
    return templates.TemplateResponse("otp.html", {"request":request})

@app.get("/userotp/{email}")
async def otp(request: Request, email:str, db: Session = Depends(get_db)):
    user=db.query(models.User).filter(models.User.user_email==email).first()
    return templates.TemplateResponse("otp.html", {"request":request, "user":user})
    
# @app.get("/inputotp/{email}/{user_otp}")
# async def otp(request: Request, email: str, user_otp: str, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.user_email == email).first()
    
#     if user:
#         if user_otp == user.otp:  # Replace 'otp_from_database' with the actual column name storing the OTP in the database
#             # OTP is correct, proceed to the next page
#             return templates.TemplateResponse("confirmpass.html", {"request": request, "user": user})
#         else:
#             # OTP is incorrect
#          message = "Otp code is incorrect. Please try again"
#         return HTMLResponse(content=f"<script>alert('{message}'); window.location='/confirmpass'</script>", status_code=401)
    
@app.get("/inputotp")
async def inputotp(request: Request, db: Session = Depends(get_db)):
    otp = request.query_params.get("otp")  # Get the OTP code from the query parameters

    # Retrieve the user based on the provided OTP code
    user = db.query(models.User).filter(models.User.otp == otp).first()

    if user:
        # Clear the old user_password
        user.user_password = ""
        db.commit()
        return templates.TemplateResponse("newpass.html", {"request": request, "success": True})
    else:
        return templates.TemplateResponse("newpass.html", {"request": request, "success": False})
    
 
# # link to confirmpass.html----------------------------------------------------------------------------------------------------------
@app.get("/confirmpass")
async def confirmpass(request: Request, db: Session = Depends(get_db)):
     user = db.query(models.User).filter(models.User.acc_status=="true").order_by(models.User.user_email.asc()).first()
     return templates.TemplateResponse("confirmpass.html", {"request": request, "user":user})
 
# @app.get("/confirmpass/{user_email}")
# async def confirmpass(request: Request, user_email:str , db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.user_ID==user_email).first()
#     return templates.TemplateResponse("confirmpass.html", {"request": request, "user": user})

# # #nachachange but only the first user, used in change pass and forgot pass
# @app.post("/change_pass/{email}")
# async def change_pass(
#     email:str,
#     new_pass: str = Form(...),
#     confirm_pass: str = Form(...),
#     db: Session = Depends(get_db)
# ):
#     user = db.query(models.User).filter(models.User.user_ID==email).first()

#     if user:
#         if new_pass == confirm_pass:
#             # Hash the new password
#             hashed_password = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())

#             # Update the user's password with the hashed password
#             user.user_password = hashed_password.decode('utf-8')

#             # Commit the changes to the database
#             db.commit()
#         else:
#             # New password and confirm password do not match
#             message = "Passwords do not match"
#             return HTMLResponse(content=f"<script>alert('{message}'); window.location='/confirmpass'</script>", status_code=401)

#     return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/change_pass")
async def change_pass(
    
    new_pass: str = Form(...),
    confirm_pass: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_ID).first()

    if user:
        if new_pass == confirm_pass:
            # Hash the new password
            hashed_password = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt())

            # Update the user's password with the hashed password
            user.user_password = hashed_password.decode('utf-8')

            # Commit the changes to the database
            db.commit()
        else:
            # New password and confirm password do not match
            message = "Passwords do not match"
            return HTMLResponse(content=f"<script>alert('{message}'); window.location='/confirmpass'</script>", status_code=401)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# ADMINSIDE=============================================================================================================================
# link to adminhome.html
# @app.post("/adminhome")
# async def adminhome(request: Request, access_token: str):
#     try:
#         payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication token")
#         # Perform any additional checks or actions based on the user's access
#         return templates.TemplateResponse("admin/adminhome.html", {"request": request,   "access_token": access_token})
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid authentication token")
    
# link to dashboard.html
#get the user count who registered dashboard
def get_user_count():
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user_count = session.query(User).filter(User.acc_status==True).count()
        return user_count
    finally:
        session.close()
#get the user count for people who lives in a street
def get_street_count(street):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        user_count = session.query(User).filter(User.street == street).count()
        return user_count
    finally:
        session.close()
     
@app.get("/dashboard")
async def dashboard(request: Request, access_token: Optional[str] = None):
    try:
        if access_token:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid authentication token")
            # Perform any additional checks or actions based on the user's access
        #fetch number of users
        user_count = get_user_count() 
         # Create data for the user count bar chart
        user_count_data = [
            go.Indicator(
                mode="number",
                value=user_count,
               title={
                        "text": "Users",
                        "font": {"color": "white"}  
                    },
                number={"font": {"size": 72, "color": "white"}}
                
            )
        ]

        # Create layout for the user count bar chart
        user_count_layout = go.Layout(
                    height=150,
                    paper_bgcolor="#012a4a",
                    plot_bgcolor="#012a4a",
                    annotations=[
                {
                    "text": "",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 50, "color": "white"}
                }
            ]
                    
                )

        # Create the user count bar chart figure
        user_count_fig = go.Figure(data=user_count_data, layout=user_count_layout)
        # Convert the user count bar chart figure to HTML
        user_count_chart_html = user_count_fig.to_html(full_html=False)
        
        # Fetch number of users registered in each street
        streets = ['Acacia St.', 'Adelaide St.', 'Adelfa St.', 'Banaba St.', 'Dahlia St.', 'Dao St.', 'Emerald St.', 'Evergreen St.','Gardenia St.','Ilang-Ilang St.']
        street_counts = [get_street_count(street) for street in streets]
        # Define data for the bar chart
        bar_data = [
            go.Bar(
                x=streets,
                y=street_counts,
                marker=dict(color='#5390d9')
            )
        ]

        # Define layout for the bar chart
        bar_layout = go.Layout(height=600,
                               paper_bgcolor="rgba(0,0,0,0)",  # Set paper background color to transparent
                               plot_bgcolor="rgba(0,0,0,0)", 
        )

        # Create the bar chart figure
        bar_fig = go.Figure(data=bar_data, layout=bar_layout)

        # Convert the bar chart figure to HTML
        bar_chart_html = bar_fig.to_html(full_html=False)

        # Define data for the pie chart
        pie_data = [
            go.Pie(
                labels=['Claimed', 'Pending'],
                values=[20, 30],
                marker=dict(colors=['#007f5f', '#d62828'])  # Change the colors to your desired values
            )
        ]

        # Define layout for the pie chart
        pie_layout = go.Layout(paper_bgcolor="rgba(0,0,0,0)",  # Set paper background color to transparent
                                plot_bgcolor="rgba(0,0,0,0)",
           
        )

        # Create the pie chart figure
        pie_fig = go.Figure(data=pie_data, layout=pie_layout)

        # Convert the pie chart figure to HTML
        pie_chart_html = pie_fig.to_html(full_html=False)

        # Render the dashboard template with the chart HTMLs and checklist
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {"request": request, "access_token": access_token, "bar_chart_html": bar_chart_html, "pie_chart_html": pie_chart_html, "user_count_chart_html":user_count_chart_html}
        )

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    

@app.post("/dashboard1")
async def dashboard(request: Request, access_token: Optional[str] = None):
    try:
        if access_token:
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid authentication token")
            # Perform any additional checks or actions based on the user's access
        #fetch number of users
        user_count = get_user_count() 
         # Create data for the user count bar chart
        user_count_data = [
            go.Indicator(
                mode="number",
                value=user_count,
               title={
                        "text": "Users",
                        "font": {"color": "white"}  
                    },
                number={"font": {"size": 72, "color": "white"}}
                
            )
        ]

        # Create layout for the user count bar chart
        user_count_layout = go.Layout(
                    height=150,
                    paper_bgcolor="#012a4a",
                    plot_bgcolor="#012a4a",
                    annotations=[
                {
                    "text": "",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 50, "color": "white"}
                }
            ]
                    
                )

        # Create the user count bar chart figure
        user_count_fig = go.Figure(data=user_count_data, layout=user_count_layout)
        # Convert the user count bar chart figure to HTML
        user_count_chart_html = user_count_fig.to_html(full_html=False)
        
        # Fetch number of users registered in each street
        streets = ['Acacia St.', 'Adelaide St.', 'Adelfa St.', 'Banaba St.', 'Dahlia St.', 'Dao St.', 'Emerald St.', 'Evergreen St.','Gardenia St.','Ilang-Ilang St.']
        street_counts = [get_street_count(street) for street in streets]
        # Define data for the bar chart
        bar_data = [
            go.Bar(
                x=streets,
                y=street_counts,
                marker=dict(color='#5390d9')
            )
        ]

        # Define layout for the bar chart
        bar_layout = go.Layout(height=600,
                               paper_bgcolor="rgba(0,0,0,0)",  # Set paper background color to transparent
                               plot_bgcolor="rgba(0,0,0,0)", 
        )

        # Create the bar chart figure
        bar_fig = go.Figure(data=bar_data, layout=bar_layout)

        # Convert the bar chart figure to HTML
        bar_chart_html = bar_fig.to_html(full_html=False)

        # Define data for the pie chart
        pie_data = [
            go.Pie(
                labels=['Claimed', 'Pending'],
                values=[20, 30],
                marker=dict(colors=['#007f5f', '#d62828'])  # Change the colors to your desired values
            )
        ]

        # Define layout for the pie chart
        pie_layout = go.Layout(paper_bgcolor="rgba(0,0,0,0)",  # Set paper background color to transparent
                                plot_bgcolor="rgba(0,0,0,0)",
           
        )

        # Create the pie chart figure
        pie_fig = go.Figure(data=pie_data, layout=pie_layout)

        # Convert the pie chart figure to HTML
        pie_chart_html = pie_fig.to_html(full_html=False)

        # Render the dashboard template with the chart HTMLs and checklist
        return templates.TemplateResponse(
            "admin/dashboard.html",
            {"request": request, "access_token": access_token, "bar_chart_html": bar_chart_html, "pie_chart_html": pie_chart_html, "user_count_chart_html":user_count_chart_html}
        )

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


#link to profiling.html---------------------------------------------------------------------------------------------------------
@app.get("/profiles")
async def profiles(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).\
        filter(models.User.acc_status == True).\
        order_by(models.User.user_ID.asc()).\
        all()
    return templates.TemplateResponse("admin/profiling.html", {"request": request, "users": users})

# delete info
@app.get("/delete/{user_id}")
async def delete(request: Request, user_id: str, db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.user_ID == user_id).first()
    # Delete the connected fund_entry records
    fund_entries = users.fund_entries
    for fund_entry in fund_entries:
        db.delete(fund_entry)
        
    db.delete(users)
    db.commit()
    return RedirectResponse(url=app.url_path_for("profiles"), status_code=status.HTTP_303_SEE_OTHER)

# link to fund entries.html-------------------------------------------------------------------------------------------------------------------
@app.get("/fundentry")
async def fundentry(request: Request):
    return templates.TemplateResponse("admin/fundentry.html", {"request": request})

@app.post("/addfund")
def add_fund(request: Request,
             fund_amount: Decimal = Form(...),
             fund_date: date = Form(...),
             db: Session = Depends(get_db)
             ):
    fund_status = "pending"  # Set fund_status to "pending"

    users_with_true_acc_status = db.query(User).filter(
        User.acc_status == True
    ).all()

    for user in users_with_true_acc_status:
        fund_rec = FundEntry(
            fund_date=fund_date,
            fund_amount=fund_amount,
            fund_status=fund_status
        )

        # Associate the FundEntry with the current user
        user.fund_entries.append(fund_rec)
        user.fund_status = "pending"

    db.commit()

    # Retrieve the updated user data from the database
    users = db.query(User).all()
    claim_status=True
    # return RedirectResponse(url=f'/fundstatus?claim_status={claim_status}', status_code=302)
    return templates.TemplateResponse("admin/fundrecords.html", {"request": request, "users": users, "claim_status":claim_status})
#fundrecords.html---------------------------------------------------------------------------------------------------------
#link to fundrec and displaying all accounts with pending fund_status
@app.get("/fundrec")
async def fundrec(request: Request, db: Session = Depends(get_db)):
    users = db.query(models.User).\
        join(models.User.fund_entries).\
        filter(models.FundEntry.fund_status == 'pending').\
        order_by(models.User.user_ID.asc()).\
        all()
    return templates.TemplateResponse("admin/fundrecords.html", {"request": request, "users": users})

# link to posts.html
@app.get("/posts")
async def posts(request: Request):
    return templates.TemplateResponse("admin/post.html", {"request": request})

# edit posts
@app.get("/edit/{a_id}")
async def edit(request: Request, a_id: int, db: Session = Depends(get_db)):
    announcements= db.query(models.Announcement).filter(models.Announcement.a_ID == a_id).first()
    return templates.TemplateResponse("editpost.html", {"request": request, "announcements":announcements})

# update info
@app.post("/update/{a_id}")
async def update(request: Request, a_id: int,
                   a_title: str = Form(...),
                    a_date: str = Form(...),
                    a_time: str = Form(...),
                    a_location: date = Form(...),
                    a_description: str = Form(...),
                 db: Session = Depends(get_db)
                 ):
    announcements= db.query(models.Announcement).filter(models.Announcement.a_ID == a_id).first()
    announcements.a_title=a_title
    announcements.a_date=a_date
    announcements.a_time=a_time
    announcements.a_location=a_location
    announcements.a_description=a_description
    db.commit()
    return RedirectResponse(url=app.url_path_for("posthistory"), status_code=status.HTTP_303_SEE_OTHER)

# delete posts
@app.get("/deletepost/{a_id}")
async def delete(request: Request, a_id: int, db: Session = Depends(get_db)):
    announcements = db.query(models.Announcement).filter(models.Announcement.a_ID == a_id).first()
    db.delete(announcements)
    db.commit()
    return RedirectResponse(url=app.url_path_for("posthistory"), status_code=status.HTTP_303_SEE_OTHER)

# Adding announcement with db
@app.post("/addannouncement")
async def addannouncement(request: Request,
                          a_title: str = Form(...),
                          a_date: date = Form(...),
                          a_time: time = Form(...),
                          a_location: str = Form(...),
                          a_description: str = Form(...),
                          db: Session = Depends(get_db)
                          ):
    posting = models.Announcement(a_title=a_title,
                                   a_date=a_date,
                                   a_time=a_time,
                                   a_location=a_location,
                                   a_description=a_description)
    db.add(posting)
    db.commit()
    return RedirectResponse(url=app.url_path_for("announcements"), status_code=status.HTTP_303_SEE_OTHER)

#link to posthistory.html to view history 
@app.get("/posthistory")
async def posthistory(request: Request, db: Session = Depends(get_db)):
    announcements = db.query(models.Announcement).\
        order_by(models.Announcement.a_ID.asc()).\
        all()
    return templates.TemplateResponse("admin/p_history.html", {"request": request, "announcements": announcements})

# link to useraccounts.html
@app.get("/accounts")
async def accounts(request: Request, db: Session = Depends(get_db)):
     users = db.query(models.User).filter(models.User.acc_status=="pending").order_by(models.User.user_ID.asc()).all()
     return templates.TemplateResponse("admin/useraccounts.html", {"request": request, "users": users})
 
#approve user account. 
class ApproveUserRequest(BaseModel):
    user_id: str
    user_password: str

# Approve user
@app.get("/approve_user/{user_id}")
async def approve_user(
    user_id: str,
    user_password: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.user_ID == user_id).first()
    if user:
        user.acc_status = True
        hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())
        user.user_password = hashed_password.decode('utf-8')
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="User not found")

    return RedirectResponse(url="/accounts", status_code=status.HTTP_303_SEE_OTHER)


 
#decline button in user will automatically delete the info of users 
@app.get("/decline_user/{user_id}")
async def decline_user(request: Request, user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_ID == user_id).first()
    db.delete(user)
    db.commit()
    
    return RedirectResponse(url="/accounts", status_code=status.HTTP_303_SEE_OTHER)


# @app.get("/decline_user/{user_id}")
# async def decline_user(request: Request, user_id: str, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.user_ID == user_id).first()
    
#     if user == True:
#             db.delete(user)
#             db.commit()
#     return RedirectResponse(url=app.url_path_for("accounts"), status_code=status.HTTP_303_SEE_OTHER)
# USERSIDE===========================================================================================================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

@app.post("/userhome")
async def userhome(request: Request, access_token: str):
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
        # Perform any additional checks or actions based on the user's access
        return templates.TemplateResponse("user/home.html", {"request": request, "access_token": access_token})
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")


# link to userhome.html
@app.get("/home")
async def home(request: Request):
    return templates.TemplateResponse("user/home.html", {"request": request})
#link to home once the button is clicked--------------------------------------------------------------------------------------------
# @app.get("/home")
# async def home(request: Request, db:Session = Depends(get_db)):
#     user = db.query(models.User).first()
#     if user:
#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(data={"sub": user.user_email}, expires_delta=access_token_expires)
#         # return {"access_token": access_token, "token_type": "bearer"}
#         redirect_url = "/home1"
#         query_params = {"access_token": access_token}

#         # Append query parameters to the redirect URL
#         if query_params:
#             encoded_params = urlencode(query_params)
#             redirect_url = f"{redirect_url}?{encoded_params}"
    
#         # Create the RedirectResponse and set the Authorization header
#         response = RedirectResponse(url=redirect_url)
#         response.headers["Authorization"] = f"Bearer {access_token}"

#         return response
    
#     else:
#         return {"error": "No admin data found in the database"}
# #after clicking the button home 
# @app.get("/home1")
# async def home1(request: Request, access_token: str):
#     try:
#         payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication token")
#         # Perform any additional checks or actions based on the user's access
#         return templates.TemplateResponse("user/home.html", {"request": request, "access_token": access_token})
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid authentication token")

    
#viewinfo---------------------------------------------------------------------------------------------------------------------------

#after clicking the button viewinfo
# @app.get("/viewinfo1")
# async def viewinfo1(request: Request, access_token: str):
#     try:
#         payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise HTTPException(status_code=401, detail="Invalid authentication token")
#         # Perform any additional checks or actions based on the user's access
#         return templates.TemplateResponse("user/viewinfo.html", {"request": request, "access_token": access_token})
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid authentication token")

#viewinfo
# @app.get("/viewinfo1")
# async def viewinfo1(request: Request,  db: Session = Depends(get_db)):
#         user_data = db.query(models.User).filter(models.User.user_email).order_by(models.User.user_ID).first()
#         return templates.TemplateResponse("user/viewinfo.html", {"request": request, "user_data": user_data})
    
# link to status.html------------------------------------------------------------------------------------------------------------------


# @app.get("/fundstatus", response_class=HTMLResponse)
# async def fund_status(request: Request, claim_status: bool = False):
#     return templates.TemplateResponse("user/fundstatus.html", {"request": request, "claim_status": claim_status})
# @app.get("/fundstatus", response_class=HTMLResponse)
# async def fund_status(request: Request, claim_status: bool = Query(default=False)):
#     return templates.TemplateResponse("user/fundstatus.html", {"request": request, "claim_status": claim_status})
@app.get("/fundstatus")
async def fundstatus(request: Request, claim_status=HTMLResponse):
    if claim_status==True:
       return templates.TemplateResponse("user/fundstatus.html", {"request": request, "claim_status": [claim_status]})
    else:
        return templates.TemplateResponse("user/fundstatus.html", {"request": request})
# link to announcements.html------------------------------------------------------------------------------------------------------------------
@app.get("/announcements")
async def announcements(request: Request, db: Session = Depends(get_db)):
    announcements = db.query(models.Announcement).\
         order_by(models.Announcement.a_ID.desc()).\
         first()
    return templates.TemplateResponse("user/announcements.html", {"request": request, "announcements": [announcements]})

# link to viewinfo.html------------------------------------------------------------------------------------------------------------------
@app.get("/viewinfo")
async def viewinfo(request: Request, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_ID).first()
    return templates.TemplateResponse("user/viewinfo.html", {"request": request, "user": user})

@app.get("/viewinfo/{user_id}")
async def viewinfo(request: Request, user_id: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_ID == user_id).first()
    return templates.TemplateResponse("user/viewinfo.html", {"request": request, "user": user})


#Termsandcondition====================================================================================================================
@app.get("/agreement")
async def agreement(request: Request):
    return templates.TemplateResponse("agreement.html", {"request": request})

@app.get("/userhome1")
async def userhome1(request: Request):
    return templates.TemplateResponse("user/home.html", {"request": request})