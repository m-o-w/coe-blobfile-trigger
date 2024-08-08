import json

def generate_exchange_rates(json_content: str) -> list:
    data = json.loads(json_content)
    base_currency = data['source']
    quotes = data['quotes']
    timestamp = data['timestamp']

    exchange_rates = []

    # Calculate exchange rates between all possible currency pairs
    for from_currency, from_rate in quotes.items():
        from_currency = from_currency[len(base_currency):]  # Extract target currency from key
        for to_currency, to_rate in quotes.items():
            to_currency = to_currency[len(base_currency):]  # Extract target currency from key
            if from_currency != to_currency:
                rate = (1 / from_rate) * to_rate
                exchange_rates.append({
                    "base_currency": from_currency,
                    "target_currency": to_currency,
                    "date": timestamp,
                    "exchange_rate": rate
                })

    return exchange_rates
