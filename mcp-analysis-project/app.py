import json
from fastmcp import FastMCP
from textblob import TextBlob

mcp = FastMCP("Sentiment Analysis Service")

@mcp.tool()
def sentiment_analysis(text: str) -> str:
    """Analyze the sentiment of the provided text."""
    blob = TextBlob(text)
    sentiment = blob.sentiment
    
    result = {
        "polarity": round(sentiment.polarity, 2),  # -1 (negative) to 1 (positive)
        "subjectivity": round(sentiment.subjectivity, 2),  # 0 (objective) to 1 (subjective)
        "assessment": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
    }

    return json.dumps(result)

@mcp.prompt()
def sentiment_prompt(text: str) -> str:
    """Create a sentiment analysis prompt."""
    return f"""You are a sentiment analysis expert. Analyze the sentiment of the following text: "{text}"."""

if __name__ == "__main__":
    mcp.run(transport="http",
    host="0.0.0.0",           # Bind to all interfaces
    port=8000,                # Custom port
    log_level="DEBUG")