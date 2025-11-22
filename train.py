import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from dotenv import load_dotenv
from perplexity import Perplexity

# Load environment variables
load_dotenv()
api_key = os.getenv('PERPLEXITY_API_KEY')
client = Perplexity(api_key=api_key)

# Load dataset
df = pd.read_csv('Truth_Seeker_Model_Dataset.csv')
# Filter NA if needed
df = df.dropna(subset=[
    'author', 'statement', 'target', 'BinaryNumTarget',
    'manual_keywords', 'tweet', '5_label_majority_answer', '3_label_majority_answer'
])

# Features and label
feature_columns = [
    'author',           # Categorical
    'statement',        # Text
    'manual_keywords',  # Text/Keywords
    'tweet'             # Tweet Text
]
X_text = df['tweet'].astype(str)
y = df['BinaryNumTarget'].astype(int)  # 1: True/Real, 0: Fake

# Vectorize tweet text (you can concatenate statement and keywords if preferred)
vectorizer = TfidfVectorizer(stop_words='english', max_features=4000)
X = vectorizer.fit_transform(X_text)

# Model training
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, y_train)

# Evaluation
y_pred = clf.predict(X_test)
print(classification_report(y_test, y_pred))

# Save the model and vectorizer
joblib.dump(clf, 'model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
print("Model and vectorizer saved to disk.")

# Perplexity API prediction example
def classify_with_perplexity(statement, tweet):
    prompt = (
        "You are a fake news expert. Statement: '{}'. Tweet: '{}'. "
        "Classify if the tweet shares real or fake news (return 'Real' or 'Fake' with confidence score)."
    ).format(statement, tweet)
    response = client.chat.completions.create(
        model="sonar-pro",
        messages=[
            {"role": "system", "content": "Fake news classifier."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Example usage
sample_row = df.iloc[0]
perplexity_result = classify_with_perplexity(
    sample_row['statement'],
    sample_row['tweet']
)
print("Perplexity API result:", perplexity_result)
