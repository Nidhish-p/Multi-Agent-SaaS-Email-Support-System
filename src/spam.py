import joblib
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer
import os
from dotenv import load_dotenv
import nltk

# Load model and vectorizer
load_dotenv()

class SpamClassifier:
    def __init__(self):
        # self.model = joblib.load(os.getenv("MODEL_PATH"))
        # self.vectorizer = joblib.load(os.getenv("VECTORIZER"))
        model_path = os.getenv("MODEL_PATH")
        vectorizer_path = os.getenv("VECTORIZER")
        
        self.model = joblib.load(model_path)
        self.vectorizer = joblib.load(vectorizer_path)

    def _transform_text(self,text):
        text = text.lower()
        text = nltk.word_tokenize(text)
        y = []
        for i in text:
            if i.isalnum():
                y.append(i)
        text = y[:]
        y.clear()
        for i in text:
            if i not in stopwords.words('english') and i not in string.punctuation:
                y.append(i)
        y = list(map(lambda x: PorterStemmer().stem(x), y))
        y = " ".join(y)
        return y

    def check(self,email):
        clean_email = self._transform_text(email)
        features = self.vectorizer.transform([clean_email])
        prediction = self.model.predict(features)
        return prediction[0] == 1