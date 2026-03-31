import requests

def check_grammar(text: str) -> dict:
    """
    Calls the free LanguageTool API to check grammar and formats the response
    with user-friendly corrections.
    """
    endpoint = "https://api.languagetool.org/v2/check"
    params = {
        "text": text,
        "language": "en-US",
    }
    
    try:
        response = requests.post(endpoint, data=params, timeout=10)
        response.raise_for_status()
        raw_result = response.json()

        # Format the response to include user-friendly corrections
        formatted_result = format_grammar_suggestions(text, raw_result)
        return formatted_result

    except requests.exceptions.RequestException as e:
        # Raise an exception to be caught by the FastAPI route
        raise RuntimeError(f"LanguageTool API request failed: {e}")

def format_grammar_suggestions(original_text: str, raw_result: dict) -> dict:
    """
    Formats the LanguageTool response to include user-friendly corrections
    and specific suggestions for each error.
    """
    suggestions = []

    for match in raw_result.get("matches", []):
        offset = match.get("offset", 0)
        length = match.get("length", 0)
        error_text = original_text[offset:offset + length]

        # Get the error context (some characters before and after)
        context_start = max(0, offset - 20)
        context_end = min(len(original_text), offset + length + 20)
        context = original_text[context_start:context_end]

        # Get possible replacements
        replacements = []
        for replacement in match.get("replacements", []):
            replacements.append(replacement.get("value", ""))

        # Format the suggestion
        suggestion = {
            "error_type": match.get("rule", {}).get("category", {}).get("name", "Grammar"),
            "message": match.get("message", ""),
            "error_text": error_text,
            "context": context,
            "offset": offset,
            "length": length,
            "possible_corrections": replacements[:3] if replacements else ["No specific correction available"],
            "suggested_correction": replacements[0] if replacements else None,
            "rule_id": match.get("rule", {}).get("id", ""),
            "short_message": match.get("shortMessage", match.get("message", ""))
        }

        suggestions.append(suggestion)

    return {
        "original_text": original_text,
        "total_errors": len(suggestions),
        "suggestions": suggestions,
        "has_errors": len(suggestions) > 0,
        "message": f"Found {len(suggestions)} grammar issue(s)" if len(suggestions) > 0 else "No grammar issues found!"
    }

