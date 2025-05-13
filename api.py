from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
from bson import ObjectId

from categorize_mails import categorizer_mails, categorized_mails, collection, today
from send_mail import *
from take_mails import *


app = FastAPI()
    
     
class ConnectMailRequest(BaseModel):
    user_email: str


class MailSample(BaseModel):
    _id: str
    date: str

class TodayMail(BaseModel):
    total_documents: int
    sample_data: List[MailSample]


class DeleteMailsRequest(BaseModel):
    mail_ids: List[str]

class DeleteResponse(BaseModel):
    message: str
    deleted_count: int
    failed_ids: List[str] = []



profile = None


@app.post("/mails/connect_mail")
def connect_mail(request: ConnectMailRequest):
    global profile
    service = authenticate_gmail()
    profile = service.users().getProfile(userId='me').execute()
    return profile
        


@app.get("/today_mails", response_model=TodayMail)
def today_mails():
    all_data = list(collection.find({}, {"_id": 1, "date": 1}))
    for item in all_data:
        item["_id"] = str(item["_id"])
    return {
        "total_documents": len(all_data),
        "sample_data": all_data[:-8] if all_data else []
    }



@app.post("/mails/insert_mails_into_database")
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
    query = {} if category.lower() == "all" else {"predicted_class": category}
    mails = list(collection.find(query, {"_id": 0}))
    if not mails:
        raise HTTPException(status_code=404, detail="Bu kategoriye ait mail bulunamadı.")
    return {"mails": mails}



@app.post("/mails/send_mail")
def send_mail_other_user(to: str, subject: str, body: str):
    global profile
    if profile is None:
        raise HTTPException(status_code=401, detail="Lütfen önce mail ile giriş yapınız.")
    service = authenticate_gmail()
    user_email = profile.get("emailAddress")
    send_email(service, to, subject, body)
    return "E-posta başarıyla gönderildi."




@app.delete("/mails/delete-selected", response_model=DeleteResponse)
async def delete_selected_mails(request: DeleteMailsRequest):
    try:
        deleted_count = 0
        failed_ids = []
        
        for mail_id in request.mail_ids:
            try:
                result = collection.delete_one({"id": mail_id})
                if result.deleted_count > 0:
                    deleted_count += 1
                else:
                    failed_ids.append(mail_id)
            except Exception as e:
                failed_ids.append(mail_id)
                print(f"Mail silme hatası (ID: {mail_id}): {str(e)}")
        
        return DeleteResponse(
            message=f"{deleted_count} adet mail başarıyla silindi. {len(failed_ids)} adet mail silinemedi.",
            deleted_count=deleted_count,
            failed_ids=failed_ids
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True )