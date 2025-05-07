from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
import uvicorn
from import_mails_to_mongodb import import_data_into_mongodb, categorized_mails, collection
from send_mail import *
from take_mails import *



app = FastAPI()
    
     
class ConnectMailRequest(BaseModel):
    user_email: str


profile = None



@app.post("/mails/connect_mail")
def connect_mail(request: ConnectMailRequest):
    global profile
    service = authenticate_gmail(request.user_email)
    profile = service.users().getProfile(userId='me').execute()
    return profile
        


@app.post("/mails/import_data_into_mongodb")
def import_data():
    import_data_into_mongodb()
    if categorized_mails:
        collection.insert_many(categorized_mails)
        return f"{len(categorized_mails)} e-posta başarıyla MongoDB Atlas'a yüklendi."
    else:
        return "Yüklenecek e-posta bulunamadı."


@app.get("/mails/{category}")
def get_mails_by_category(category: str):
    query = {} if category.lower() == "all" else {"predicted_class": category}
    mails = list(collection.find(query, {"_id": 0}))
    if not mails:
        raise HTTPException(status_code=404, detail="Bu kategoriye ait mail bulunamadı.")
    
    return {"mails": mails}



@app.post("/mails/{send_mail}")
def send_mail_other_user(request: ConnectMailRequest, to : str, subject:str, body:str ):
    global profile
    service = authenticate_gmail(request.user_email)
    send_email(service, to, subject, body)
    return "E-posta başarıyla gönderildi."



if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True )