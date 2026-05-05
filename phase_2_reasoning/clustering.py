from sklearn.feature_extraction.text import TfidfVectorizer
import umap.umap_ as umap
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from typing import List, Dict, Any
from scrubber import PIIScrubber

class ReviewClusterer:
    """Handles embedding and clustering of review texts."""
    
    def __init__(self, use_tfidf: bool = True):
        # Using a lightweight TF-IDF vectorizer to avoid PyTorch Windows DLL issues
        print("Initializing TF-IDF vectorizer...")
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scrubber = PIIScrubber()
        
    def cluster_reviews(self, raw_reviews: List[str]) -> Dict[int, List[str]]:
        """
        Takes raw reviews, scrubs them, embeds them, reduces dimensions, and clusters.
        Returns a dictionary mapping cluster_id to a list of scrubbed review texts.
        cluster_id -1 represents outliers (noise).
        """
        if not raw_reviews:
            return {}
            
        print("Scrubbing PII from reviews...")
        scrubbed_texts = [self.scrubber.scrub(text) for text in raw_reviews]
        
        # If very few reviews, just return them as one cluster
        if len(scrubbed_texts) < 5:
            return {0: scrubbed_texts}
            
        print("Generating embeddings via TF-IDF...")
        # Tfidf returns a sparse matrix, UMAP accepts sparse matrices but it's easier to convert to dense for small datasets
        embeddings = self.vectorizer.fit_transform(scrubbed_texts).toarray()
        
        print("Reducing dimensions with UMAP...")
        # UMAP parameters tuned for small-to-medium text datasets
        n_neighbors = min(15, len(embeddings) - 1)
        umap_embeddings = umap.UMAP(
            n_neighbors=n_neighbors, 
            n_components=5, 
            metric='cosine',
            random_state=42
        ).fit_transform(embeddings)
        
        print("Clustering with AgglomerativeClustering...")
        # Agglomerative parameters - using distance threshold
        clusterer = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=1.5, # Adjust based on UMAP scaling
            metric='euclidean',
            linkage='ward'
        )
        cluster_labels = clusterer.fit_predict(umap_embeddings)
        
        # Group reviews by cluster label
        clusters: Dict[int, List[str]] = {}
        for idx, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(scrubbed_texts[idx])
            
        return clusters
