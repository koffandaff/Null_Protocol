import Api from '../api.js';
import Utils from '../utils.js';
import Auth from '../auth.js';
import Components from '../components.js';

class ChatView {
    constructor() {
        this.currentSessionId = null;
        this.sessions = [];
        this.isStreaming = false;
        this.abortController = null; // For stop streaming
    }

    async render() {
        return `
            ${Components.renderNavbar()}
            <div style="display: flex; height: 100vh; padding-top: 60px;">
                <!-- Sidebar: Session List -->
                <div id="chat-sidebar" style="width: 280px; background: rgba(0,0,0,0.4); border-right: 1px solid rgba(255,255,255,0.05); display: flex; flex-direction: column; overflow: hidden;">
                    <!-- New Chat Button -->
                    <div style="padding: 1rem;">
                        <button id="new-chat-btn" class="btn" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                            <i class="material-symbols-outlined" style="font-size: 1.2rem;">add</i>
                            NEW CHAT
                        </button>
                    </div>
                    
                    <!-- Session List -->
                    <div id="session-list" style="flex: 1; overflow-y: auto; padding: 0 0.5rem;">
                        <div style="color: var(--text-muted); text-align: center; padding: 2rem 0.5rem; font-size: 0.8rem;">
                            Loading sessions...
                        </div>
                    </div>
                    
                    <!-- Ollama Status -->
                    <div id="ollama-status" style="padding: 0.8rem; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.7rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #666;"></span>
                        <span>Checking Ollama...</span>
                    </div>
                </div>
                
                <!-- Main Chat Area -->
                <div style="flex: 1; display: flex; flex-direction: column; overflow: hidden;">
                    <!-- Chat Header -->
                    <div id="chat-header" style="padding: 1rem 1.5rem; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 1rem;">
                            <a href="#/dashboard" class="btn-outline btn-sm" style="display: flex; align-items: center; justify-content: center; padding: 0.5rem; border: none; color: var(--text-muted);" title="Go to Dashboard">
                                <i class="material-symbols-outlined" style="font-size: 1.5rem;">home</i>
                            </a>
                            <div>
                                <div style="display: flex; align-items: center; gap: 0.5rem;">
                                    <h2 id="chat-title" style="margin: 0; font-size: 1.1rem; color: var(--text);">AI Assistant</h2>
                                    <button id="edit-title-btn" class="btn-outline btn-sm" style="padding: 2px; border: none; color: var(--text-muted); display: none;" title="Edit Title">
                                        <i class="material-symbols-outlined" style="font-size: 1rem;">edit</i>
                                    </button>
                                </div>
                                <div id="chat-subtitle" style="font-size: 0.75rem; color: var(--text-muted);">Powered by Koffan/Cybiz</div>
                            </div>
                        </div>
                        <button id="delete-session-btn" class="btn-outline btn-sm" style="display: none;">
                            <i class="material-symbols-outlined" style="font-size: 1rem;">delete</i>
                        </button>
                    </div>

                    
                    <!-- Messages Container -->
                    <div id="messages-container" style="flex: 1; overflow-y: auto; padding: 1.5rem;">
                        <div id="messages-list" style="max-width: 800px; margin: 0 auto;">
                            <!-- Welcome message when empty -->
                            <div id="welcome-message" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                                <i class="material-symbols-outlined" style="font-size: 4rem; color: var(--primary); opacity: 0.5;">smart_toy</i>
                                <h3 style="margin-top: 1rem; color: var(--text);">Welcome to Cybiz AI</h3>
                                <p style="font-size: 0.9rem;">Start a conversation or select a previous chat from the sidebar.</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Input Area -->
                    <div style="padding: 1rem 1.5rem; border-top: 1px solid rgba(255,255,255,0.05); background: rgba(0,0,0,0.2);">
                        <form id="chat-form" style="max-width: 800px; margin: 0 auto; display: flex; gap: 0.8rem;">
                            <input type="text" id="message-input" placeholder="Type your message..." style="flex: 1;" autocomplete="off">
                            <button type="submit" id="send-btn" class="btn" style="padding: 0.8rem 1.5rem;">
                                <i class="material-symbols-outlined" style="font-size: 1.2rem;">send</i>
                            </button>
                            <button type="button" id="stop-btn" class="btn" style="padding: 0.8rem 1.5rem; display: none; background: #ff4757;">
                                <i class="material-symbols-outlined" style="font-size: 1.2rem;">stop</i>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        `;
    }

    async afterRender() {
        document.getElementById('logout-btn').addEventListener('click', () => Auth.logout());

        // Load sessions and check Ollama
        await this.loadSessions();
        await this.checkOllamaStatus();

        // Event Listeners
        document.getElementById('new-chat-btn').addEventListener('click', () => this.createNewChat());
        document.getElementById('chat-form').addEventListener('submit', (e) => this.handleSendMessage(e));
        document.getElementById('delete-session-btn').addEventListener('click', () => this.deleteCurrentSession());
        document.getElementById('edit-title-btn').addEventListener('click', () => this.editTitle());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopStreaming());
    }

    async loadSessions() {
        try {
            const response = await Api.get('/chat/sessions');
            this.sessions = response || [];
            this.renderSessionList();
        } catch (error) {
            console.error('Failed to load sessions:', error);
            document.getElementById('session-list').innerHTML = `
                <div style="color: #ff4757; padding: 1rem; font-size: 0.8rem;">Failed to load sessions</div>
            `;
        }
    }

    renderSessionList() {
        const container = document.getElementById('session-list');

        if (this.sessions.length === 0) {
            container.innerHTML = `
                <div style="color: var(--text-muted); text-align: center; padding: 2rem 0.5rem; font-size: 0.8rem;">
                    No conversations yet.<br>Start a new chat!
                </div>
            `;
            return;
        }

        container.innerHTML = this.sessions.map(s => `
            <div class="session-item ${s.id === this.currentSessionId ? 'active' : ''}" 
                 data-session-id="${s.id}"
                 style="padding: 0.8rem; margin: 0.3rem 0; border-radius: 8px; cursor: pointer; background: ${s.id === this.currentSessionId ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255,255,255,0.02)'}; border-left: 3px solid ${s.id === this.currentSessionId ? 'var(--primary)' : 'transparent'}; transition: all 0.2s; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1; overflow: hidden;">
                    <div style="font-size: 0.85rem; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${Utils.escapeHtml(s.title)}</div>
                    <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.2rem;">${s.message_count} messages</div>
                </div>
                <button class="delete-session-item" data-session-id="${s.id}" style="background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 0.25rem; opacity: 0.5;" title="Delete">
                    <i class="material-symbols-outlined" style="font-size: 1rem;">close</i>
                </button>
            </div>
        `).join('');

        // Add click listeners for session selection
        container.querySelectorAll('.session-item').forEach(item => {
            item.addEventListener('click', (e) => {
                // Don't select if clicking delete button
                if (e.target.closest('.delete-session-item')) return;
                const sessionId = item.dataset.sessionId;
                this.loadSession(sessionId);
            });
        });

        // Add click listeners for delete buttons
        container.querySelectorAll('.delete-session-item').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                e.stopPropagation();
                const sessionId = btn.dataset.sessionId;
                if (confirm('Delete this conversation?')) {
                    try {
                        await Api.delete(`/chat/sessions/${sessionId}`);
                        if (this.currentSessionId === sessionId) {
                            this.currentSessionId = null;
                            this.createNewChat();
                        }
                        await this.loadSessions();
                        Utils.showToast('Deleted', 'success');
                    } catch (err) {
                        Utils.showToast('Failed to delete', 'error');
                    }
                }
            });
        });
    }

    async loadSession(sessionId) {
        try {
            const session = await Api.get(`/chat/sessions/${sessionId}`);
            this.currentSessionId = sessionId;
            this.renderSessionList();
            this.renderMessages(session.messages);

            document.getElementById('chat-title').textContent = session.title;
            document.getElementById('delete-session-btn').style.display = 'block';
            document.getElementById('edit-title-btn').style.display = 'block';
            document.getElementById('welcome-message').style.display = 'none';
        } catch (error) {
            Utils.showToast('Failed to load session', 'error');
        }
    }

    renderMessages(messages) {
        const container = document.getElementById('messages-list');

        if (messages.length === 0) {
            container.innerHTML = `<div id="welcome-message" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="material-symbols-outlined" style="font-size: 4rem; color: var(--primary); opacity: 0.5;">chat</i>
                <p style="margin-top: 1rem;">This conversation is empty. Send a message to begin.</p>
            </div>`;
            return;
        }

        container.innerHTML = messages.map((m, i) => this.renderSingleMessage(m, i)).join('');
        this.scrollToBottom();
    }

    renderSingleMessage(message, index) {
        const isUser = message.role === 'user';
        const formattedContent = this.formatMessageContent(message.content);

        return `
            <div class="chat-message ${isUser ? 'user' : 'assistant'}" style="margin-bottom: 1.5rem; display: flex; gap: 1rem; flex-direction: ${isUser ? 'row-reverse' : 'row'};">
                <div class="avatar" style="width: 36px; height: 36px; border-radius: 50%; background: ${isUser ? 'var(--primary)' : 'var(--secondary)'}; display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <i class="material-symbols-outlined" style="font-size: 1.2rem; color: #000;">${isUser ? 'person' : 'smart_toy'}</i>
                </div>
                <div class="message-content" style="flex: 1; max-width: 85%;">
                    <div class="message-bubble" style="background: ${isUser ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255,255,255,0.03)'}; padding: 1rem; border-radius: 12px; border-top-${isUser ? 'right' : 'left'}-radius: 4px; position: relative;">
                        <div class="message-text" style="line-height: 1.6; font-size: 0.9rem;">${formattedContent}</div>
                        <button class="copy-btn" onclick="copyMessage(this)" style="position: absolute; top: 0.5rem; right: 0.5rem; background: transparent; border: none; color: var(--text-muted); cursor: pointer; opacity: 0.5; transition: opacity 0.2s;" title="Copy">
                            <i class="material-symbols-outlined" style="font-size: 1rem;">content_copy</i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    formatMessageContent(content) {
        // Escape HTML first
        let formatted = Utils.escapeHtml(content);

        // Code blocks (```language...```)
        formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
            return `<pre class="code-block" style="background: rgba(0,0,0,0.4); padding: 1rem; border-radius: 8px; overflow-x: auto; margin: 0.5rem 0; position: relative;"><code class="language-${lang || 'plaintext'}">${code.trim()}</code><button onclick="copyCode(this)" style="position: absolute; top: 0.5rem; right: 0.5rem; background: rgba(255,255,255,0.1); border: none; color: var(--text-muted); padding: 0.3rem 0.5rem; border-radius: 4px; cursor: pointer; font-size: 0.7rem;">COPY</button></pre>`;
        });

        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.4rem; border-radius: 4px; font-family: JetBrains Mono, monospace;">$1</code>');

        // Bold
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

        // Italic
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    async handleSendMessage(e) {
        e.preventDefault();

        const input = document.getElementById('message-input');
        const message = input.value.trim();

        if (!message || this.isStreaming) return;

        input.value = '';
        this.isStreaming = true;
        document.getElementById('send-btn').disabled = true;

        // Hide welcome message
        const welcome = document.getElementById('welcome-message');
        if (welcome) welcome.style.display = 'none';

        // Add user message to UI
        const messagesContainer = document.getElementById('messages-list');
        messagesContainer.insertAdjacentHTML('beforeend', this.renderSingleMessage({ role: 'user', content: message }, 0));

        // Add assistant placeholder
        const assistantId = 'assistant-' + Date.now();
        messagesContainer.insertAdjacentHTML('beforeend', `
            <div id="${assistantId}" class="chat-message assistant" style="margin-bottom: 1.5rem; display: flex; gap: 1rem;">
                <div class="avatar" style="width: 36px; height: 36px; border-radius: 50%; background: var(--secondary); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                    <i class="material-symbols-outlined" style="font-size: 1.2rem; color: #000;">smart_toy</i>
                </div>
                <div class="message-content" style="flex: 1; max-width: 85%;">
                    <div class="message-bubble" style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 12px; border-top-left-radius: 4px;">
                        <div class="message-text streaming" style="line-height: 1.6; font-size: 0.9rem;">
                            <span class="typing-indicator">●●●</span>
                        </div>
                    </div>
                </div>
            </div>
        `);
        this.scrollToBottom();

        // Send to API with SSE
        this.abortController = new AbortController();
        document.getElementById('send-btn').style.display = 'none';
        document.getElementById('stop-btn').style.display = 'block';

        try {
            const token = localStorage.getItem('access_token');
            const response = await fetch(`${Api.baseUrl}/chat/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    session_id: this.currentSessionId,
                    message: message
                }),
                signal: this.abortController.signal
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            const messageTextEl = document.querySelector(`#${assistantId} .message-text`);
            let fullContent = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                const lines = text.split('\n').filter(line => line.startsWith('data: '));

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.session_id && data.type === 'session_created') {
                            this.currentSessionId = data.session_id;
                            document.getElementById('delete-session-btn').style.display = 'block';
                            document.getElementById('edit-title-btn').style.display = 'block';
                            // Update title immediately
                            document.getElementById('chat-title').textContent = message.slice(0, 30) + (message.length > 30 ? '...' : '');
                            await this.loadSessions();
                        }

                        if (data.content) {
                            fullContent += data.content;
                            messageTextEl.innerHTML = this.formatMessageContent(fullContent);
                            this.scrollToBottom();
                        }

                        if (data.error) {
                            messageTextEl.innerHTML = `<span style="color: #ff4757;"><i class="material-symbols-outlined" style="vertical-align: middle;">error</i> ${data.error}</span>`;
                        }

                        if (data.type === 'done') {
                            // Add copy button
                            const bubble = messageTextEl.parentElement;
                            const copyBtn = document.createElement('button');
                            copyBtn.className = 'copy-btn';
                            copyBtn.innerHTML = '<i class="material-symbols-outlined" style="font-size: 1rem;">content_copy</i>';
                            copyBtn.onclick = () => window.copyMessage(copyBtn);
                            copyBtn.style.cssText = 'position: absolute; top: 0.5rem; right: 0.5rem; background: transparent; border: none; color: var(--text-muted); cursor: pointer; opacity: 0.5;';
                            bubble.style.position = 'relative';
                            bubble.appendChild(copyBtn);
                        }
                    } catch (err) {
                        console.error('Parse error:', err);
                    }
                }
            }

            // Reload sessions to update titles
            await this.loadSessions();

        } catch (error) {
            if (error.name !== 'AbortError') {
                Utils.showToast('Failed to send message: ' + error.message, 'error');
            }
        } finally {
            this.isStreaming = false;
            this.abortController = null;
            document.getElementById('send-btn').style.display = 'block';
            document.getElementById('send-btn').disabled = false;
            document.getElementById('stop-btn').style.display = 'none';
        }
    }

    stopStreaming() {
        if (this.abortController) {
            this.abortController.abort();
        }
    }

    async createNewChat() {
        this.currentSessionId = null;
        this.renderSessionList();

        document.getElementById('chat-title').textContent = 'New Conversation';
        document.getElementById('delete-session-btn').style.display = 'none';
        document.getElementById('edit-title-btn').style.display = 'none';
        document.getElementById('messages-list').innerHTML = `
            <div id="welcome-message" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                <i class="material-symbols-outlined" style="font-size: 4rem; color: var(--primary); opacity: 0.5;">smart_toy</i>
                <h3 style="margin-top: 1rem; color: var(--text);">Start a New Conversation</h3>
                <p style="font-size: 0.9rem;">Type your message below to begin chatting with Cybiz AI.</p>
            </div>
        `;
    }

    async editTitle() {
        if (!this.currentSessionId) return;

        const currentTitle = document.getElementById('chat-title').textContent;
        const newTitle = prompt('Enter new conversation title:', currentTitle);

        if (newTitle && newTitle.trim() && newTitle !== currentTitle) {
            try {
                await Api.put(`/chat/sessions/${this.currentSessionId}/title`, { title: newTitle.trim() });
                document.getElementById('chat-title').textContent = newTitle.trim();
                await this.loadSessions();
                Utils.showToast('Title updated', 'success');
            } catch (error) {
                Utils.showToast('Failed to update title', 'error');
            }
        }
    }

    async deleteCurrentSession() {
        if (!this.currentSessionId) return;

        if (!confirm('Delete this conversation?')) return;

        try {
            await Api.delete(`/chat/sessions/${this.currentSessionId}`);
            Utils.showToast('Conversation deleted', 'success');
            this.currentSessionId = null;
            await this.loadSessions();
            this.createNewChat();
        } catch (error) {
            Utils.showToast('Failed to delete', 'error');
        }
    }

    async checkOllamaStatus() {
        const statusEl = document.getElementById('ollama-status');
        try {
            const data = await Api.get('/chat/health');
            if (data.ollama_connected && data.model_available) {
                statusEl.innerHTML = `
                    <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: var(--primary);"></span>
                    <span style="color: var(--primary);">AI: Ready</span>
                `;
            } else if (data.ollama_connected && !data.model_available) {
                statusEl.innerHTML = `
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <div style="display: flex; align-items: center; gap: 0.5rem;">
                            <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #ffa502;"></span>
                            <span style="color: #ffa502;">Model Missing</span>
                        </div>
                        <div style="font-size: 0.6rem; color: var(--text-muted); opacity: 0.8;">Check Ollama models</div>
                    </div>
                `;
            } else {
                statusEl.innerHTML = `
                    <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #ff4757;"></span>
                    <span style="color: #ff4757;">Ollama Offline</span>
                `;
            }
        } catch {
            statusEl.innerHTML = `
                <span class="status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #666;"></span>
                <span style="color: #666;">Status Unknown</span>
            `;
        }
    }

    scrollToBottom() {
        const container = document.getElementById('messages-container');
        container.scrollTop = container.scrollHeight;
    }
}

// Global functions for copy buttons
window.copyMessage = function (btn) {
    const text = btn.parentElement.querySelector('.message-text').innerText;
    navigator.clipboard.writeText(text).then(() => {
        btn.innerHTML = '<i class="material-symbols-outlined" style="font-size: 1rem;">check</i>';
        setTimeout(() => {
            btn.innerHTML = '<i class="material-symbols-outlined" style="font-size: 1rem;">content_copy</i>';
        }, 2000);
    });
};

window.copyCode = function (btn) {
    const code = btn.parentElement.querySelector('code').innerText;
    navigator.clipboard.writeText(code).then(() => {
        btn.textContent = 'COPIED!';
        setTimeout(() => { btn.textContent = 'COPY'; }, 2000);
    });
};

export default new ChatView();
