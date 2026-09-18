def predict(query: str) -> dict:
    """Return the stable subsystem and priority prediction contract."""
    text = query.casefold()

    # TEMPORARY DUMMY MODEL
    # Replace only this prediction logic when the trained NLP model is available.
    if any(keyword in text for keyword in ("payment", "taka", "টাকা", "card")):
        return {
            "subsystem": "Payment",
            "priority": "High",
        }

    if any(keyword in text for keyword in ("delivery", "late", "order ashe nai", "পাইনি")):
        return {
            "subsystem": "Delivery",
            "priority": "High",
        }

    if any(keyword in text for keyword in ("damaged", "broken", "wrong product")):
        return {
            "subsystem": "Product",
            "priority": "Medium",
        }

    return {
        "subsystem": "Technical Support",
        "priority": "Low",
    }