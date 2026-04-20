# Simple in-memory storage (no dependencies)

memory_store = []

def store_policy(text, doc_id):
    memory_store.append(text)

def retrieve_policy(query):
    # simple retrieval (first 2 docs)
    return "\n".join(memory_store[:2])
