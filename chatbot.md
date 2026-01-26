# AI Chatbot Implementation Guide

This document details the technical implementation of the AI Chatbot integrated into the Fsociety platform.

## Architecture Overview

The chatbot is built using a client-server architecture with real-time streaming capabilities.

### Backend
- **Framework**: FastAPI (Python)
- **AI Engine**: Ollama (local)
- **Model**: `IHA089/drana-infinity-3b:3b` (configurable in `Chat_Service.py`)
- **Communication**: Server-Sent Events (SSE) for streaming
- **Persistence**: JSON-based file storage (`backend/data/chat_sessions.json`)

### Frontend
- **Framework**: Vanilla JavaScript (Component-based)
- **State Management**: Local class-based state in `ChatView`
- **Styling**: Vanilla CSS (Glassmorphism design system)
- **Icons**: Material Symbols Outlined

## Technical Components

### 1. Chat Models (`backend/model/Chat_Model.py`)
Defines the data structure for chat messages and sessions.
- `ChatMessage`: Role (user/assistant), content, and timestamp.
- `ChatSession`: Unique ID, user ID, title, and message history.
- `ChatDatabase`: Handles CRUD operations for sessions using a JSON file.

### 2. Chat Service (`backend/service/Chat_Service.py`)
The bridge between the API and Ollama.
- `send_message_stream`: Orchestrates the flow:
  1. Retrieves or creates a session.
  2. Saves the user message.
  3. Prepares the system prompt and context (last 10 messages).
  4. Calls Ollama API with `stream: true`.
  5. Yields chunks to the router.
  6. Saves the full assistant response once finished.

### 3. Chat Router (`backend/routers/Chat_Router.py`)
Exposes protected API endpoints.
- `GET /sessions`: List user's conversations.
- `GET /sessions/{id}`: Get full conversation history.
- `DELETE /sessions/{id}`: Remove a conversation.
- `PUT /sessions/{id}/title`: Edit a conversation title.
- `POST /send`: Send a message and initiate SSE stream.
- `GET /health`: Check Ollama and model availability.

### 4. Frontend View (`frontend/js/views/chat.js`)
High-performance UI implementation.
- **Streaming Logic**: Uses the Fetch API with `ReadableStream` to process incoming tokens in real-time.
- **Markdown Rendering**: Custom regex-based formatter for code blocks, bold, italics, and line breaks.
- **Session Sidebar**: Dynamic listing of conversations with auto-updating titles and inline delete buttons.
- **Title Editing**: Allows users to rename their conversations via edit button.
- **Stop Button**: Allows users to abort ongoing AI responses mid-stream.

## Setup & Requirements

1. **Ollama**: Must be installed and running locally (`ollama serve`).
2. **Model**: Ensure atleast one model is available. List with:
   ```bash
   ollama list
   ```
3. **Authentication**: All chat endpoints require a valid JWT token in the `Authorization` header.

## Features implemented

- [x] **Real-time Streaming**: Character-by-character response delivery.
- [x] **Context Awareness**: Remembers previous messages in the session.
- [x] **Code Highlighting**: Formats technical code blocks with a copy button.
- [x] **Session Persistence**: Saves all chats locally.
- [x] **Dynamic Titles**: Automatically generates titles based on the first message.
- [x] **Title Editing**: Manual override for conversation names via edit icon.
- [x] **Health Monitoring**: Visual indicator of Ollama status.
- [x] **Stop Streaming**: Red stop button to abort AI responses mid-generation.
- [x] **Session Deletion**: Delete individual sessions from sidebar or header.
- [x] **Session Switching**: Click any session in sidebar to load its history.

## Changing the AI Model

To use a different Ollama model, update the model name in:
```python
# backend/service/Chat_Service.py line 17
self.model = "your-model-name:tag"
```

---
*Created by Antigravity for the Fsociety Platform.*
