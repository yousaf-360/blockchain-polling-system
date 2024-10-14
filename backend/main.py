from fastapi import FastAPI, HTTPException, APIRouter, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from pydantic import BaseModel
import uvicorn
import uuid
from datetime import timedelta
from schemas import UserCreate, UserLogin, UserResponse, PollCreate
from models import User, Poll
from database import db
from utils import get_password_hash, verify_password, create_access_token,get_current_user
from typing import List

ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    user_dict = user.dict()
    user_dict["_id"] = str(uuid.uuid4())
    user_dict["password"] = get_password_hash(user.password)

    if db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already registered")

    db.users.insert_one(user_dict)
    return UserResponse(**user_dict)

@router.post("/login")
def login(user: UserLogin):
    db_user = db.users.find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": db_user["username"]}, expires_delta=access_token_expires)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**db_user)
    }


import json
with open('../build/contracts/PollingSystem.json', 'r') as file:
    data = json.load(file)

contract_abi = data['abi']
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
contract_address = '0xe770e47C8fee273117a8e5A14a2D6E863CaAf483'

class PollRequest(BaseModel):
    question: str
    options: List[str]

@app.post("/create_poll")
def create_poll(
    poll: PollRequest,  
    private_key: str = Header(...), 
    current_user: User = Depends(get_current_user) 
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")

    try:
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)

        account = w3.eth.account.from_key(private_key)
        print("Private key : ",private_key)
        print("polls info : ",poll.question, poll.options)
        print("account : ",account)

        transaction = contract.functions.createPoll(poll.question, poll.options).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)

        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        return {"transaction_hash": tx_hash.hex()}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Assuming PollRequest and User are defined earlier in your code
class PollResponse(BaseModel):
    id: int
    question: str
    options: List[str]

@router.get("/get_polls", response_model=List[PollResponse])
def get_polls(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")

    try:
        # Create contract instance
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)

        # Get all poll questions from the contract
        questions = contract.functions.getAllPolls().call()

        # Prepare a list to hold the poll responses
        polls = []

        for i, question in enumerate(questions):
            # Get poll details
            poll = contract.functions.getPoll(i).call()
            print(i,poll)
            poll_response = PollResponse(id=i,question=poll[0], options=poll[1])
            polls.append(poll_response)

        return polls

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class VoteRequest(BaseModel):
    poll_id: int
    option_id: int

class VoteResponse(BaseModel):
    has_voted: bool
    results: List[int]

@router.post("/vote", response_model=VoteResponse)
def vote(vote_request: VoteRequest, private_key: str = Header(...), current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authorized")

    try:
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        account = w3.eth.account.from_key(private_key)

        # Check if the user has already voted
        has_voted = contract.functions.hasUserVoted(vote_request.poll_id, account.address).call()

        if has_voted:
            # Retrieve results if the user has already voted
            results = contract.functions.getResults(vote_request.poll_id).call()
            return {"has_voted": True, "results": results}

        # Build the transaction for voting
        transaction = contract.functions.vote(vote_request.poll_id, vote_request.option_id).build_transaction({
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gas': 2000000
        })

        # Sign and send the transaction
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Wait for the transaction receipt (optional)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        # After voting, retrieve results
        results = contract.functions.getResults(vote_request.poll_id).call()

        return {"has_voted": False, "results": results}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



app.include_router(router)

