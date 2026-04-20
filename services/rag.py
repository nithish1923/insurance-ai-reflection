from db.vectordb import retrieve_policy

def get_policy_context(query):
    return retrieve_policy(query)
