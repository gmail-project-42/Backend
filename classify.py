from take_mails import * 
from google import genai
from google.genai import types
from pydantic import BaseModel
import os
from dotenv import load_dotenv


list_of_daily_mails, service, list_of_body, snippet = return_mails_and_service()


class classes_of_mails(BaseModel):
    pazarlama_reklam_bildirim: bool
    bilgilendirme_eposta: bool
    abonelik_bildirim: bool
    fatura_finansal_bildirim: bool
    supheli_icerik: bool
    sosyal:bool



def load_client():
    load_dotenv()  
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY ortam değişkeni tanımlı değil!")
    client = genai.Client(api_key=GEMINI_API_KEY)
    return client



def classify_mail(mail_content):
    client = load_client()
    
    prompt = f"""
    Aşağıdaki e-posta içeriğini şu kategorilerden birine sınıflandır:
    
    pazarlama_reklam_bildirim
    bilgilendirme_eposta
    abonelik_bildirim
    fatura_finansal_bildirim
    supheli_icerik (güvenlik)
    sosyal medya
    
    E-posta içeriği:
    {mail_content}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents='Give me class for mail',
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
            response_schema=classes_of_mails,
        ),
    )
    return response.text



def classify_main():
    for mail_body in list_of_body:
        response = classify_mail(mail_body)
        print(response)
        
        
        
if __name__ == "__main__":
    classify_main()