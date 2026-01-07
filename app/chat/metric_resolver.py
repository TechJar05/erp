from app.chat.metric_aliases import METRIC_ALIASES

def resolve_metric(domain_key: str, user_query: str) -> str | None:
    query = user_query.lower()
    domain = METRIC_ALIASES.get(domain_key)

    if not domain:
        return None

    for metric, phrases in domain.items():
        for phrase in phrases:
            if phrase in query:
                return metric

    return None
