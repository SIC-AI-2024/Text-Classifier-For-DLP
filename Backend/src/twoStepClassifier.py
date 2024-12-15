from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import re
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
class TwoStepClassifier:
    def __init__(self, vectorizer, classifier_1, classifier_2, corpora_features):
        self.vectorizer = vectorizer
        self.classifier_1 = classifier_1
        self.classifier_2 = classifier_2
        self.corpora_features = corpora_features  # Dict with corpora names as keys and feature matrices as values


    def replace_sensitive_info(self, text):
        """Mask sensitive information in the text."""
        text = re.sub(r'\+977[-.\s]?\d{10}', 'PHONE_NUM', text)
        text = re.sub(r'\b(?:\d{4}[-.\s]?)\d{4}[-.\s]?\d{4}[-.\s]?\d{4}\b', 'CREDIT_CARD', text)
        text = re.sub(r'\b\d{9,20}\b', 'ACCOUNT_NUM', text)
        text = re.sub(r'\b\d{2}/\d{2}\b', 'EXPIRY_DATE', text)
        text = re.sub(r'\b\d{3}\b', 'CVC_CODE', text)
        return text

    def preprocess_text(self, text):
        """Preprocess text (remove sensitive info, tokenize, lowercased, etc.)."""
        stop_words = set(stopwords.words('english'))
        stemmer = PorterStemmer()
        text = ' '.join(text.split())
        text = self.replace_sensitive_info(text)
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\sPHONE_NUMCREDIT_CARDACCOUNT_NUMEXPIRY_DATECVC_CODE]', '', text)
        words = word_tokenize(text)
        words = [stemmer.stem(word) for word in words if word not in stop_words]
        return ' '.join(words)

    def predict(self, X):
        """
        Predict probabilities and determine sensitive corpora resemblance.

        :param X: Input feature matrix (array of text data).
        :return: Dictionary with classification probabilities and resemblance details.
        """
        if isinstance(X, list):
            X = np.array(X)

        X_processed = [self.preprocess_text(text) for text in X]
        X_vectorized = self.vectorizer.transform(X_processed)
       
        
        # Step 1: Classify Non-Enterprise vs. Enterprise
        step_1_probs = self.classifier_1.predict_proba(X_vectorized)

        final_probs = np.zeros((X.shape[0], 3))  # 3 classes: Non-Enterprise, Sensitive, Non-Sensitive
        final_probs[:, 0] = step_1_probs[:, 0]  # Non-Enterprise

        # Identify enterprise-related documents
        enterprise_indices = np.where(np.argmax(step_1_probs, axis=1) == 1)[0]

        resemblance_results = [None] * X.shape[0]

        if len(enterprise_indices) > 0:
            enterprise_features = X_vectorized[enterprise_indices]
            step_2_probs = self.classifier_2.predict_proba(enterprise_features)

            final_probs[enterprise_indices, 1] = step_2_probs[:, 1]  # Sensitive
            final_probs[enterprise_indices, 2] = step_2_probs[:, 0]  # Non-Sensitive

            # Check resemblance for sensitive documents
            sensitive_indices = enterprise_indices[np.argmax(step_2_probs, axis=1) == 1]

            for idx in sensitive_indices:
                similarities = {}
                doc_vector = X_vectorized[idx]

                # Compute similarity with each corpus
                for corpus_name, corpus_features in self.corpora_features.items():
                    similarity = cosine_similarity(doc_vector, corpus_features).mean()
                    similarities[corpus_name] = similarity

                # Find the most similar corpus
                most_similar_corpus = max(similarities, key=similarities.get)
                resemblance_results[idx] = {
                    "most_similar_corpus": most_similar_corpus,
                    "similarity_scores": similarities,
                }

        return {
            "probabilities": final_probs.tolist(),
            "resemblance": resemblance_results
        }


