from transformers import pipeline
import numpy as np

class MailClassifier:
    def __init__(self):
        # Zero-shot sınıflandırma pipeline'ını yükle
        self.classifier = pipeline("zero-shot-classification",
                                 model="facebook/bart-large-mnli",
                                 device="cpu")
        
        # Sınıf etiketlerini tanımla
        self.labels = [
            "İş ve Profesyonel",
            "Kişisel İletişim",
            "Pazarlama ve Reklam",
            "Bildirim ve Uyarılar",
            "Spam ve İstenmeyen",
            "Finansal",
            "Diğer"
        ]
    
    def classify_mail(self, mail_content):
        """
        E-posta içeriğini sınıflandır
        
        Args:
            mail_content (str): E-posta içeriği
            
        Returns:
            dict: Sınıflandırma sonucu ve güven skorları
        """
        # Zero-shot sınıflandırma yap
        result = self.classifier(mail_content, 
                               candidate_labels=self.labels,
                               multi_label=False)
        
        # En yüksek skorlu sınıfı ve skorunu al
        predicted_class = result['labels'][0]
        confidence_score = result['scores'][0]
        
        return {
            'predicted_class': predicted_class,
            'confidence_score': confidence_score,
            'all_scores': dict(zip(result['labels'], result['scores']))
        }

# Kullanım örneği
if __name__ == "__main__":
    classifier = MailClassifier()
    
    # Örnek e-posta içeriği
    sample_mail = """
    Sayın müşterimiz,
    
    Kredi kartı limitiniz 5000 TL artırılmıştır. Detaylar için internet bankacılığını
    ziyaret edebilirsiniz.
    
    Saygılarımızla,
    XYZ Bank
    """
    
    # Sınıflandırma yap
    result = classifier.classify_mail(sample_mail)
    
    print(f"Tahmin edilen sınıf: {result['predicted_class']}")
    print(f"Güven skoru: {result['confidence_score']:.2f}")
    print("\nTüm sınıflar için skorlar:")
    for class_name, score in result['all_scores'].items():
        print(f"{class_name}: {score:.2f}") 