import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection("policy_docs")

def store_policy(text, doc_id):
    collection.add(documents=[text], ids=[doc_id])

def retrieve_policy(query):
    results = collection.query(query_texts=[query], n_results=2)
    if results["documents"]:
        return "\n".join(results["documents"][0])
    return ""
