from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from bson import ObjectId
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()


origins = ["*"]  

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MONGO_URI = os.getenv("MONGO_URI")
db_name = os.getenv("dataBaseName")
collection_name = os.getenv("collectionName")
client = MongoClient(MONGO_URI)
db = client[db_name]
tasks_collection = db[collection_name]

class Task(BaseModel):
    title:str
    completed:bool = False


def task_serializer(task) -> dict:
    return {
        "id": str(task["_id"]),
        "title": task["title"],
        "completed": task["completed"]
    }


@app.get("/")
def hello():
    return {"message": "Hello, Welcome In Todo Manager"}

@app.get("/tasks")
def get_tasks():
    tasks = tasks_collection.find()
    return [task_serializer(task) for task in tasks]

@app.post("/tasks")
def add_task(task:Task):
    task_dict = task.dict()
    result = tasks_collection.insert_one(task_dict)
    new_task = tasks_collection.find_one({"_id": result.inserted_id})
    return task_serializer(new_task)

@app.put("/tasks/{id}")
def update_task(id:str, task:Task):
    task_dict = task.dict()
    tasks_collection.update_one({"_id": ObjectId(id)}, {"$set": task_dict})
    updated_task = tasks_collection.find_one({"_id": ObjectId(id)})
    return task_serializer(updated_task)


@app.delete("/tasks/{id}")
def delete_task(id:str):
    tasks_collection.delete_one({"_id": ObjectId(id)})
    return {"message": "Task deleted successfully"}