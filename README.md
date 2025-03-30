# Gmail Proje

Bu proje, Gmail API kullanarak e-postaları almak, sınıflandırmak ve yönetmek için geliştirilmiş bir Python uygulamasıdır.

## Özellikler

- Gmail API kullanarak günlük e-postaları alma
- E-posta içeriklerini sınıflandırma
  - Transformers kütüphanesi ile zero-shot sınıflandırma
  - Google Gemini API ile sınıflandırma
- E-posta gönderme

## Kurulum

1. Gerekli kütüphaneleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

2. Google Cloud Console'dan bir proje oluşturun ve Gmail API'yi etkinleştirin.
3. `credentials.json` dosyasını indirin ve proje klasörüne yerleştirin.
4. `.env` dosyasında Gemini API anahtarınızı ayarlayın.

## Kullanım

### E-postaları Alma
```python
python take_mails.py
```

### E-postaları Sınıflandırma
```python
python mail_classifier.py
```

veya 

```python
python classify.py
```

### E-posta Gönderme
```python
python send_mail.py
```

## Dosya Açıklamaları

- `mail_classifier.py`: Transformers kütüphanesi ile e-posta sınıflandırma
- `take_mails.py`: Gmail API kullanarak e-postaları alma
- `classify.py`: Google Gemini API ile e-posta sınıflandırma
- `send_mail.py`: Gmail API kullanarak e-posta gönderme
- `requirements.txt`: Gerekli Python kütüphaneleri 