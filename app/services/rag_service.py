import uuid

from app.services import llm_service, embedding_service
from app.retrieval import retriever, reranker
from app.config import settings

# In-memory conversation storage: {"conversation_id": [{"role": "...", "content": "..."}]}
CONVERSATIONS: dict[str, list[dict]] = {}


async def chat(msg: str, conversation_id: str | None = None) -> dict :

    # 1. Manage Conversation ID
    if not conversation_id or conversation_id not in CONVERSATIONS :
        conversation_id = str(uuid.uuid4())[:8]
        CONVERSATIONS[conversation_id] = []

    history = CONVERSATIONS[conversation_id]

    # 2. Retrieve relevant chunks for current question
    infos = await retriever.retrieval(msg)

    context_arr = [chunk[2] for chunk in infos]
    sources = [chunk[4]["source"] for chunk in infos if "source" in chunk[4]]
    subjects = [chunk[4]["subject"] for chunk in infos if "subject" in chunk[4]]
    renranked_context = await reranker.reranker(msg, context_arr)
    context = "\n".join([chunk["candidate"] for chunk in renranked_context])

    # 3. Build Messages Array with History + Context + Question
    system_instruction = (
        "You are a precise technical AI assistant. "
        "Answer the user's question using the conversation history and provided context below. "
        "If the information is not present or cannot be inferred, state: "
        "'The provided context doesn't contain sufficient information to answer this question.'"
    )
    messages = [{"role": "system", "content": system_instruction}]

    # Inject past turns
    messages.extend(history)

    # Inject current turn with context
    current_user_content = f"Context:\n{context}\n\nUser Question:\n{msg}"
    messages.append({"role": "user", "content": current_user_content})

    # 4. Query Ollama
    payload = {
        "model": settings.LARGE_LANGUAGE_MODEL,
        "messages": messages,
        "temperature": 0.1,
        "stream": False
    }

    answer = await llm_service.query_llm(payload)

    # 5. Save turn into memory (store clean prompt without context clutter)
    history.append({"role": "user", "content": msg})
    history.append({"role": "assistant", "content": answer})
    

    return {
            "conversation_id": conversation_id,
            "response": answer,
            "sources": list(dict.fromkeys(sources)),
            "subjects": list(dict.fromkeys(subjects))
        }




