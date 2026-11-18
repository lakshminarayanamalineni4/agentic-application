from fastapi import FastAPI, requests, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import UserCreate, UserUpdate, UserResponse, ChatRequest, ChatResponse
from app.models import User,Base
from app.config import DATABASE_URL
from app.database import engine, get_db
from app.services.chat import ChatService
from app.services.agent import Agent

app = FastAPI()

Base.metadata.create_all(bind=engine)
chatservice = ChatService()
agent = Agent()
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    name = user.name
    mobile = user.mobile
    email = user.email
    password = user.password

    existing_mobile = (db.query(User).filter(User.mobile==mobile).first())
    if existing_mobile:
        raise HTTPException(status_code=409, detail="Mobile exists")

    existing_email= (db.query(User).filter(User.email==email).first())

    if existing_email: 
        raise HTTPException(status_code=409, detail="email exists")

    new_user = User(
        name = name,
        mobile = mobile,
        email = email,
        password = password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).all()

    return users

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # answer = chatservice.chat(chatservice.extract_message(request))
        answer = agent.chat(request.message)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"error: {str(e)}")