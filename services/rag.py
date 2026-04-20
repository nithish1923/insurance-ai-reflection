from db.vectordb import retrieve_policy

def get_policy_context(query):
    enhanced_query = "insured name policy holder details coverage claim " + query
    return retrieve_policy(enhanced_query)
