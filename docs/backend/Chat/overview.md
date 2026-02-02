# 🤖 AI Chat Module

This document explains how the AI security assistant works in Fsociety.

---

## Overview

The AI Chat module provides an intelligent security assistant powered by local LLM:

- **Ollama Integration**: Uses locally running LLM models
- **Security Focus**: System prompt tuned for cybersecurity
- **Session Management**: Persistent chat history
- **Streaming Responses**: Real-time token streaming

---

## Architecture

```
Frontend                 Backend                    Ollama
┌──────────┐      ┌─────────────────┐      ┌──────────────┐
│ ChatView │ ───▶ │ Chat_Router.py  │ ───▶ │ localhost:   │
│          │      │                 │      │ 11434        │
│ Message  │      │ Chat_Service.py │      │              │
│ Stream   │◀──── │                 │◀──── │ LLM Model    │
└──────────┘      └─────────────────┘      │ (llama2/3)   │
                                           └──────────────┘
```

---

## Files

| File | Purpose |
|------|---------|
| `routers/Chat_Router.py` | API endpoints |
| `service/Chat_Service.py` | Business logic |
| `model/Chat_Model.py` | Pydantic schemas |

---

## API Endpoints

### Send Message
```http
POST /api/chat/message
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "uuid",
  "message": "How do I scan for open ports?"
}
```

### Response (Streaming)
```
data: {"content": "To scan"}
data: {"content": " for open"}
data: {"content": " ports,"}
...
data: [DONE]
```

### Get Sessions
```http
GET /api/chat/sessions
Authorization: Bearer <token>
```

---

## System Prompt

```python
SECURITY_SYSTEM_PROMPT = """
You are a cybersecurity expert AI assistant for Fsociety.
Your role is to help users with:
- Network security and scanning
- Vulnerability assessment
- Security best practices
- Threat analysis
- General cybersecurity questions

Guidelines:
1. Always prioritize ethical security practices
2. Do not assist with malicious activities
3. Recommend proper authorization before testing
4. Provide detailed, actionable advice
5. Reference industry standards when applicable
"""
```

---

## Code Flow

```python
# service/Chat_Service.py

async def send_message(self, user_id: str, session_id: str, message: str):
    """Send message and stream response"""
    
    # 1. Get or create session
    session = self.get_or_create_session(user_id, session_id)
    
    # 2. Get conversation history
    history = self.get_session_messages(session_id)
    
    # 3. Build messages array
    messages = [
        {"role": "system", "content": SECURITY_SYSTEM_PROMPT}
    ]
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": message})
    
    # 4. Call Ollama API
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "http://localhost:11434/api/chat",
            json={"model": "llama2", "messages": messages},
            timeout=60.0
        ) as response:
            full_response = ""
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("message", {}).get("content", "")
                    full_response += chunk
                    yield {"content": chunk}
    
    # 5. Save messages to database
    self.save_message(session_id, "user", message)
    self.save_message(session_id, "assistant", full_response)
```

---

## Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama2

# Verify running
curl http://localhost:11434/api/tags
```

---

## Related Documentation

- [Ollama Documentation](https://ollama.ai/docs)
- [Auth System](../Auth/overview.md)
