def precompute_corpora_features(corpus_files, vectorizer):
    corpora_features = {}
    for corpus_name, file_path in corpus_files.items():
        with open(file_path, "r") as f:
            corpus_text = f.readlines()
        corpus_vectorized = vectorizer.transform(corpus_text)
        corpora_features[corpus_name] = corpus_vectorized
    return corpora_features

corpus_files = {  # Map corpus names to file paths
    "dyncorp_private": "./drive/MyDrive/ADS Project/Corpora/Cleaned Corpora/dyncorp_private.csv",
    # Add other corpora paths
}

corpora_features = precompute_corpora_features(corpus_files, vectorizer)
two_step_classifier = TwoStepClassifier(vectorizer, classifier_1, classifier_2, corpora_features)
