import joblib
from nltk.corpus import stopwords
import string
from nltk.stem.porter import PorterStemmer

# Load model and vectorizer
model = joblib.load("models/spam_classifier.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

class SpamClassifier:
    def __init__(self):
        self.model = model
        self.vectorizer = vectorizer 

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