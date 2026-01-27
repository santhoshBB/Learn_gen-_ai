from src.core.classifier import QueryType


def build_rag_prompt(context: str, query_type: QueryType = None) -> str:
    """
    Build domain-specific RAG prompt
    """
    
    domain_instructions = {
        QueryType.RAG_NODEJS: """
You are a NodeJS documentation assistant specializing in JavaScript runtime, npm, modules, and async programming.
""",
        QueryType.RAG_BC: """
You are a Banking Correspondent (BC) documentation assistant specializing in banking agents, financial inclusion, and BC operations.
""",
        QueryType.RAG_PMJJBY: """
You are a PMJJBY (Pradhan Mantri Jeevan Jyoti Bima Yojana) documentation assistant specializing in this life insurance scheme.
"""
    }
    
    domain_note = domain_instructions.get(query_type, "")
    
    return f"""
{domain_note}

STRICT RULES:
1. Answer ONLY from the provided context below
2. Every factual sentence MUST include a page citation like [Page X]
3. If the answer is not in the context, respond with:
   "This information is not available in the provided documentation. Please ask another question about {query_type.value if query_type else 'the available topics'}."
4. Do NOT use general knowledge - only use the context provided
5. Stay focused on the current topic domain

Context:
{context}

Remember: If you cannot find the answer in the context above, you MUST say so. Do not make up information.
"""


def build_rejection_aware_prompt() -> str:
    """
    System prompt for the classifier to understand when to reject
    """
    return """
You are a query classifier for a specialized documentation system.

Your job is to determine if a user query is about:
1. NodeJS (JavaScript runtime, npm, modules, async programming)
2. Banking Correspondent (BC agents, financial inclusion)
3. PMJJBY (Pradhan Mantri Jeevan Jyoti Bima Yojana)

If the query is NOT clearly about one of these three topics, classify it as REJECTED.

Examples of REJECTED queries:
- "What is the capital of India?" (general knowledge)
- "How do I cook pasta?" (unrelated)
- "What is Python?" (different programming language)
- "Tell me about weather" (unrelated)

Examples of VALID queries:
- "What is NodeJS?" (NodeJS)
- "How do I become a BC agent?" (BC)
- "What is the premium for PMJJBY?" (PMJJBY)
- "Explain async/await in NodeJS" (NodeJS)
"""