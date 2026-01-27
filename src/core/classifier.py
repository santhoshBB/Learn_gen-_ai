from enum import Enum
from typing import Optional, Tuple
from langchain_qdrant import QdrantVectorStore
from src.db.qdrant_client import get_vector_store


class QueryType(str, Enum):
    REJECTED   = "rejected"      # Off-topic queries
    RAG_NODEJS = "rag_nodejs"
    RAG_BC     = "rag_bc"
    RAG_PMJJBY = "rag_pmjjby"


class DomainClassifier:
    """
    Two-stage classifier:
    1. Check if query is relevant to our domains (NodeJS, BC, PMJJBY)
    2. Route to appropriate domain based on context + similarity
    """
    
    RAG_COLLECTION = "combined-ingest"
    RAG_SCORE_THRESHOLD = 0.77
    DOMAIN_KEYWORDS = {
        QueryType.RAG_NODEJS: [
            "node", "nodejs", "javascript", "npm", "express", "async",
            "callback", "promise", "module", "package", "runtime", "v8"
        ],
        QueryType.RAG_BC: [
            "banking correspondent", "bc", "business correspondent",
            "agent", "banking agent", "financial inclusion", "correspondent"
        ],
        QueryType.RAG_PMJJBY: [
            "pmjjby", "pradhan mantri jeevan jyoti bima yojana",
            "life insurance", "term insurance", "jeevan jyoti"
        ]
    }
    
    def __init__(self):
        self.vs: QdrantVectorStore = get_vector_store(self.RAG_COLLECTION)
    
    def classify_query(
        self,
        user_query: str,
        current_domain: Optional[QueryType] = None,
        config: dict | None = None
    ) -> Tuple[QueryType, float]:
        """
        Returns (QueryType, confidence_score)
        
        Logic:
        1. If we're in a conversation context (current_domain exists):
           - Check if query is a follow-up (pronouns, context-dependent)
           - If yes, stay in current domain
           - If no, classify fresh
        
        2. For fresh classification:
           - Run similarity search
           - Check if top result exceeds threshold AND matches our domains
           - Also check keyword matching as backup
        """
        try:
            query_lower = user_query.lower()
            
            # Stage 1: Check if it's a follow-up question in current context
            if current_domain and current_domain != QueryType.REJECTED:
                if self._is_followup_question(user_query):
                    return current_domain, 1.0  # High confidence, stay in domain
            
            # Stage 2: Fresh classification via similarity search
            results = self.vs.similarity_search_with_relevance_scores(
                query=user_query,
                k=5,  # Get top 5 to check domain consistency
                score_threshold=self.RAG_SCORE_THRESHOLD,
            )
            
            if not results:
                # No relevant documents found - check keywords as fallback
                keyword_domain = self._keyword_match(query_lower)
                if keyword_domain:
                    return keyword_domain, 0.6  # Lower confidence
                return QueryType.REJECTED, 0.0
            
            # Analyze top results for domain consistency
            doc, score = results[0]
            source = doc.metadata.get("source", "").lower()
            
            # Determine domain from top result
            detected_domain = self._extract_domain_from_source(source)
            
            if detected_domain == QueryType.REJECTED:
                # Unknown source - reject
                return QueryType.REJECTED, 0.0
            
            # Verify domain consistency in top results
            domain_votes = self._count_domain_votes(results)
            if domain_votes.get(detected_domain, 0) >= 3:
                # Strong consensus
                return detected_domain, score
            elif domain_votes.get(detected_domain, 0) >= 2:
                # Moderate consensus
                return detected_domain, score * 0.8
            else:
                # Weak consensus - might be noise
                keyword_domain = self._keyword_match(query_lower)
                if keyword_domain:
                    return keyword_domain, 0.65
                return QueryType.REJECTED, 0.0
        
        except Exception as e:
            # Fail closed - reject unknown queries
            print(e)
            return QueryType.REJECTED, 0.0
    
    def _is_followup_question(self, query: str) -> bool:
        """
        Detect if query is a follow-up (context-dependent) question
        """
        query_lower = query.lower().strip()
        
        followup_indicators = [
            # Pronouns
            "it", "its", "this", "that", "these", "those", "they", "them",
            # Context-dependent phrases
            "what about", "how about", "tell me more", "explain",
            "what is the", "what are the", "how do", "can you",
            # Question words without explicit topic
            query_lower.startswith(("what", "how", "why", "when", "where", "who"))
            and len(query.split()) < 6  # Short questions likely contextual
        ]
        
        # Check if query contains pronouns or context indicators
        for indicator in followup_indicators[:8]:  # Check string indicators
            if indicator in query_lower:
                return True
        
        # Check for short questions (likely follow-ups)
        if len(query.split()) <= 5 and query_lower.startswith(("what", "how", "why")):
            # Make sure it doesn't contain domain-specific keywords
            has_domain_keyword = any(
                keyword in query_lower
                for keywords in self.DOMAIN_KEYWORDS.values()
                for keyword in keywords
            )
            if not has_domain_keyword:
                return True
        
        return False
    
    def _keyword_match(self, query_lower: str) -> Optional[QueryType]:
        """
        Fallback keyword matching for domain detection
        """
        domain_scores = {}
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in query_lower)
            if matches > 0:
                domain_scores[domain] = matches
        
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            return best_domain
        
        return None
    
    def _extract_domain_from_source(self, source: str) -> QueryType:
        """
        Map source metadata to domain
        """
        if "nodejs" in source:
            return QueryType.RAG_NODEJS
        
        if any(x in source for x in ["bc", "faq_on_bc", "banking_correspondent"]):
            return QueryType.RAG_BC
        
        if "pmjjby" in source:
            return QueryType.RAG_PMJJBY
        
        return QueryType.REJECTED
    
    def _count_domain_votes(self, results: list) -> dict:
        """
        Count how many top results belong to each domain
        """
        votes = {}
        for doc, score in results:
            source = doc.metadata.get("source", "").lower()
            domain = self._extract_domain_from_source(source)
            if domain != QueryType.REJECTED:
                votes[domain] = votes.get(domain, 0) + 1
        return votes


# Factory function for backward compatibility
def classify_query(
    user_query: str,
    config: dict | None = None,
    current_domain: Optional[QueryType] = None
) -> QueryType:
    """
    Backward-compatible wrapper
    """
    classifier = DomainClassifier()
    domain, confidence = classifier.classify_query(user_query, current_domain, config)
    return domain