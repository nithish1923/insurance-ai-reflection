# Simple in-memory storage (no external dependencies)

memory_store = []

def store_policy(text, doc_id):
    memory_store.append(text)

def retrieve_policy(query):
    return "\n".join(memory_store[:2])
