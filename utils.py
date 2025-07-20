import uuid

def generate_session_id():
    return str(uuid.uuid4())[:8]  # Shortened UUID for readability