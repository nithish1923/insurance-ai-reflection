from db.vectordb import retrieve_policy

def get_policy_context(query):
    # 🔥 Enhanced query for better retrieval
    enhanced_query = "insurance claim rules coverage limits exclusions liability " + query
    return retrieve_policy(enhanced_query)
