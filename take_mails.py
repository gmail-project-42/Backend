# Gerekli kütüphaneleri içe aktar
import os
import base64
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta, timezone


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

list_of_daily_mails = []
list_of_body = []
list_of_snippets = []




def get_text_from_payload(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                return base64.urlsafe_b64decode(data).decode('utf-8')
    elif payload['mimeType'] == 'text/plain':
        data = payload['body']['data']
        return base64.urlsafe_b64decode(data).decode('utf-8')
    return None







def authenticate_gmail(user_email):
    creds = None
    token_file = f'token_{user_email}.json'
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        if not set(SCOPES).issubset(set(creds.scopes)):
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print("Token yenileme sırasında hata oluştu:", str(e))
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)




def strip_html_tags(html):
    """
    HTML etiketlerini temizler ve düz metin döndürür.
    """
    clean = re.compile('<.*?>')
    return re.sub(clean, '', html)



def get_body_from_payload(payload):
    """
    Mesajın payload bilgisinden plain text içeriği çıkarır.
    
    Eğer 'text/plain' bulunursa onu kullanır, yoksa 'text/html' içeriğinden HTML etiketlerini kaldırır.
    """
    # Eğer mesajın parçaları varsa
    if 'parts' in payload:
        plain_text = None
        html_text = None
        for part in payload['parts']:
            mimeType = part.get('mimeType')
            body_data = part.get('body', {}).get('data')
            if body_data:
                decoded_data = base64.urlsafe_b64decode(body_data).decode('utf-8')
                if mimeType == 'text/plain' and not plain_text:
                    plain_text = decoded_data
                elif mimeType == 'text/html' and not html_text:
                    html_text = decoded_data
        if plain_text:
            return plain_text
        elif html_text:
            return strip_html_tags(html_text)
        else:
            return "İçerik alınamadı."
    else:
        # Tek parça mesajlarda
        body_data = payload.get('body', {}).get('data')
        if body_data:
            decoded_data = base64.urlsafe_b64decode(body_data).decode('utf-8')
            # Eğer payload tipi text/html ise, HTML etiketlerini temizleyelim
            if payload.get('mimeType') == 'text/html':
                return strip_html_tags(decoded_data)
            return decoded_data
        else:
            return "İçerik alınamadı."
        
        

def take_daily_mails(service):
    
    global list_of_daily_mails
    global list_of_body
    global list_of_snippets
    
    
    service = authenticate_gmail()
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    today_utc = today.astimezone(timezone.utc)
    tomorrow_utc = tomorrow.astimezone(timezone.utc)

    after_ts = int(today_utc.timestamp())
    before_ts = int(tomorrow_utc.timestamp())

    query = f'after:{after_ts} before:{before_ts}'
    results = service.users().messages().list(userId='me', q=query).execute()
    mails = results.get('messages', [])
    
    if not mails:
        print("Bugün için e-posta bulunamadı.")
    else:
        print("Bugünün e-postaları:")
        for mail in mails:
            msg_id = mail['id']
            mail = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            snippet = mail.get('snippet')
            payload = mail.get('payload')
            text = get_text_from_payload(payload)
            body = get_body_from_payload(payload)
            list_of_snippets.append(snippet)
            list_of_daily_mails.append(text)
            list_of_body.append(body)
            
    return list_of_daily_mails, list_of_body, list_of_snippets



def return_mails_and_service():
    service = authenticate_gmail()
    list_of_daily_mails, list_of_body, list_of_snippets = take_daily_mails(service)
    return list_of_daily_mails, service, list_of_body, list_of_snippets



if __name__ == "__main__":
    list_of_daily_mails, service, list_of_body, list_of_snippets = return_mails_and_service()
    for l in list_of_snippets:
        print(l)
        print("-"*50)