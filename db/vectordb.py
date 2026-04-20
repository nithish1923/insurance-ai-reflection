from openai import OpenAI
import numpy as np
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

documents = []
embeddings = []

# -------- Split text into chunks --------
def split_text(text, chunk_size=300):
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

# -------- Store policy with filtering --------
def store_policy(text, doc_id):
    chunks = split_text(text)

    for chunk in chunks:

        # 🔥 FILTER ONLY IMPORTANT POLICY SECTIONS
        if any(keyword in chunk.lower() for keyword in [
            "coverage",
            "damage",
            "claim",
            "liability",
            "limit",
            "deductible",
            "exclusion",
            "condition"
        ]):

            emb = client.embeddings.create(
                model="text-embedding-3-small",
                input=chunk
            ).data[0].embedding

            documents.append(chunk)
            embeddings.append(emb)

# -------- Cosine similarity --------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -------- Retrieve best matching chunks --------
def retrieve_policy(query, top_k=3):

    if not documents:
        return "No policy data available"

    query_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    scores = []

    for i, emb in enumerate(embeddings):
        score = cosine_similarity(query_emb, emb)
        scores.append((score, documents[i]))

    scores.sort(reverse=True)

    return "\n".join([doc for _, doc in scores[:top_k]])
