from take_mails import return_mails_and_service
from mail_classifier import MailClassifier
from pymongo import MongoClient
from dotenv import load_dotenv
import os


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


def import_data_into_mongodb():
    list_of_daily_mails, service, list_of_body, snippet = return_mails_and_service()
    classifier = MailClassifier()
    global categorized_mails 
    global collection
    
    
    for i, mail_body in enumerate(list_of_body):
        result = classifier.classify_mail(mail_body)
        mail_data = {
            "body": mail_body,
            "predicted_class": result['predicted_class'],
            "confidence_score": result['confidence_score'],
            "all_scores": result['all_scores']
        }
        categorized_mails.append(mail_data)
        
if __name__ == "__main__":
    connect_to_mongodb()