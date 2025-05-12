from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from categorize_mails import categorizer_mails, categorized_mails, collection, today
from send_mail import *
from take_mails import *


app = FastAPI()
    
     
class ConnectMailRequest(BaseModel):
    user_email: str


profile = None


@app.post("/mails/connect_mail")
def connect_mail(request: ConnectMailRequest):
    global profile
    service = authenticate_gmail()
    profile = service.users().getProfile(userId='me').execute()
    return profile
        


@app.get("/check_database")
def check_database():
    all_data = list(collection.find({}, {"_id": 0}))
    return {
        "total_documents": len(all_data),
        "sample_data": all_data[:-8] if all_data else []
    }



@app.post("/mails/import_data_into_mongodb")
def import_data():
    if profile is None:
        raise HTTPException(status_code=401, detail="Lütfen önce mail ile giriş yapınız.")
    categorizer_mails()
    if categorized_mails:
        collection.insert_many(categorized_mails)
        return f"{len(categorized_mails)} e-posta başarıyla MongoDB Atlas'a yüklendi."
    else:
        return "Yüklenecek e-posta bulunamadı."


@app.get("/mails/{category}")
def get_mails_by_category(category: str):
    if profile is None:
        raise HTTPException(status_code=401, detail="Lütfen önce mail ile giriş yapınız.")
    query = {"date": today} if category.lower() == "all" else {"date": today, "predicted_class": category}
    mails = list(collection.find(query, {"_id": 0}))
    if not mails:
        raise HTTPException(status_code=404, detail="Bu kategoriye ait mail bulunamadı.")
    return {"mails": mails}



@app.post("/mails/{send_mail}")
def send_mail_other_user(request: ConnectMailRequest, to : str, subject:str, body:str ):
    global profile
    if profile is None:
        raise HTTPException(status_code=401, detail="Lütfen önce mail ile giriş yapınız.")
    service = authenticate_gmail()
    send_email(service, to, subject, body)
    return "E-posta başarıyla gönderildi."



if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True )