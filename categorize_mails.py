from take_mails import return_mails_and_service
from mail_classifier import MailClassifier
from pymongo import MongoClient
from dotenv import load_dotenv
import os

today = None
categorized_mails  = []

def connect_to_mongodb():
    load_dotenv()
    password = os.getenv("mongodb_collection_password")
    uri = f"mongodb+srv://kayailhan128:{password}@cluster0.mkigdkx.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri)
    db = client["Mail_Database"]
    collection = db["Mail"]
    return collection


collection = connect_to_mongodb()


def categorizer_mails():
    classifier = MailClassifier()
    global categorized_mails 
    global collection
    global today
    list_of_daily_mails, service, snippet, today = return_mails_and_service()
    
    for i, item in enumerate(list_of_daily_mails):
        result = classifier.classify_mail(item['body'])
        mail_data = {
            "id": item['id'],
            "text": item['text'],
            "body": item['body'],
            "snippet": item['snippet'],
            "date": item['date'].strftime("%Y-%m-%d"),
            "predicted_class": result['predicted_class'],
            "confidence_score": result['confidence_score'],
            "all_scores": result['all_scores']
        }
        categorized_mails.append(mail_data)


if __name__ == "__main__" :
    categorizer_mails()
    print(categorized_mails)     