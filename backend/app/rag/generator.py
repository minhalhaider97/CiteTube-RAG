from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from app.core.config import settings

def generate_answer(prompt: str) -> str:
    """Invoke Groq LLM via LangChain's ChatGroq to generate grounded answers."""
    api_key = getattr(settings, "GROQ_API_KEY", None)
    model_name = getattr(settings, "GROQ_CHAT_MODEL", "llama-3.3-70b-versatile")

    if not api_key:
        return "Error communicating with LLM service: GROQ_API_KEY is missing from environment variables."

    try:
        # Initialize ChatGroq
        llm = ChatGroq(
            model=model_name,
            api_key=api_key,
            temperature=0.3  # Keeps the answers close to the provided context
        )

        # Invoke using LangChain messages
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content or "Error generating response."

    except Exception as e:
        return f"Error communicating with LLM service: {str(e)}"
