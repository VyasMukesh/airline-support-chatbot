"""
Intent Classifier using Sentence Transformers for fast semantic matching
"""
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    BERT_AVAILABLE = True
except Exception as e:
    print(f"BERT not available: {e}")
    BERT_AVAILABLE = False

class IntentClassifier:
    def __init__(self):
        if not BERT_AVAILABLE:
            self.model = None
            self.intent_embeddings = {}
            print("Running in keyword-matching mode")
            return
            
        # Use a small, fast model
        print("Loading intent classification model...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            print("Intent classification model loaded successfully!")
        except Exception as e:
            print(f"Failed to load BERT model: {e}")
            self.model = None
            self.intent_embeddings = {}
            return
        
        # Define intent examples - these will be used for semantic matching
        self.intent_examples = {
            'booked_flights': [
                'show my bookings',
                'show my flights',
                'booked flights',
                'my bookings',
                'all my flights',
                'what flights do I have',
                'show me my reservations',
                'list my bookings'
            ],
            'cancel': [
                'cancel my flight',
                'cancel booking',
                'cancel trip',
                'I want to cancel',
                'cancel my reservation',
                'cancel this flight',
                'delete booking'
            ],
            'status': [
                'flight status',
                'check status',
                'status of my flight',
                'is my flight on time',
                'flight information',
                'check my flight'
            ],
            'seat': [
                'seat information',
                'my seat',
                'seat number',
                'available seats',
                'seat availability',
                'what is my seat',
                'change seat'
            ],
            'pets': [
                'pet policy',
                'can I bring my pet',
                'pets allowed',
                'travel with dog',
                'bring my cat',
                'pet travel',
                'animal policy'
            ]
        }
        
        # Pre-compute embeddings for all examples
        self.intent_embeddings = {}
        if self.model:
            for intent, examples in self.intent_examples.items():
                embeddings = self.model.encode(examples, convert_to_tensor=True)
                self.intent_embeddings[intent] = embeddings
    
    def classify(self, user_query, threshold=0.5):
        """
        Classify user query into an intent
        Returns: intent name or None if no match above threshold
        """
        # Fallback to keyword matching if BERT not available
        if self.model is None:
            return self._keyword_classify(user_query), 0.8
        
        query_embedding = self.model.encode(user_query, convert_to_tensor=True)
        
        best_intent = None
        best_score = threshold
        
        for intent, example_embeddings in self.intent_embeddings.items():
            # Calculate cosine similarity with all examples
            similarities = util.cos_sim(query_embedding, example_embeddings)[0]
            max_similarity = torch.max(similarities).item()
            
            if max_similarity > best_score:
                best_score = max_similarity
                best_intent = intent
        
        return best_intent, best_score
    
    def _keyword_classify(self, query):
        """Fallback keyword-based classification"""
        q = query.lower()
        if any(k in q for k in ['booked', 'my bookings', 'show', 'flights', 'reservations']):
            return 'booked_flights'
        if any(k in q for k in ['cancel', 'delete', 'remove']):
            return 'cancel'
        if any(k in q for k in ['status', 'on time', 'delayed', 'check flight']):
            return 'status'
        if any(k in q for k in ['seat', 'seats']):
            return 'seat'
        if any(k in q for k in ['pet', 'dog', 'cat', 'animal']):
            return 'pets'
        return None

# Global instance (loaded once)
_classifier = None

def get_intent(query):
    """
    Get intent from user query
    Returns: (intent, confidence_score)
    """
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    
    return _classifier.classify(query.lower())
