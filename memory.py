memory_store = []

def ensure_bank_exists():
    pass


def save_memory(incident_title, resolution_text):
    memory_store.append({
        "title": incident_title,
        "text": resolution_text
    })
    print(f"[Memory saved for: {incident_title}]")


def search_memory(query):
    results = []
    for item in memory_store:
        if query.lower() in item["text"].lower():
            results.append(item["text"])

    return "\n\n".join(results[:3]) if results else None
def ensure_bank_exists():
    # Placeholder (since you're not using Hindsight anymore)
    pass