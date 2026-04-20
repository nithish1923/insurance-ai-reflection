from db.vectordb import retrieve_policy

def get_policy_context(query):
    # 🔥 Include identity + rules in search
    enhanced_query = "insurance policy holder name insured details coverage claim rules " + query
    return retrieve_policy(enhanced_query)
