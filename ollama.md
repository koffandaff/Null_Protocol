# 🤖 Ollama & Ngrok Setup Guide

To ensure **Fsociety** can connect to your local Ollama instance (especially from Vercel), you need to configure Ollama to accept external connections.

## 1. Stop Ollama Completely
- Right-click the Ollama icon in your Windows System Tray (near the clock) and click **Quit**.
- Or run `Stop-Process -Name "ollama_app_v2" -Force` in PowerShell.

## 2. Configure & Start Ollama (PowerShell)
Run these commands in a **PowerShell** window. This sets Ollama to listen on all interfaces (`0.0.0.0`) and accept requests from any origin (`*`).

> **Why `*` (Allow All)?**
> We use `*` because the free version of Ngrok changes your URL every time you restart it. If you restrict it to specific URLs, you would have to update this configuration every single session. Since this is running on your local machine for development, `*` is acceptable.

```powershell
# Set Environment Variables
$env:OLLAMA_HOST = "0.0.0.0"
$env:OLLAMA_ORIGINS = "*"

# Start Ollama
ollama serve
```

*(Keep this window open!)*

---

## 3. Start Ngrok (New Terminal)
In a **new** terminal window, run Ngrok to expose port `11434`.

**Crucial:** Use the `--host-header` flag. This tricks Ollama into thinking the request is coming from `localhost`, bypassing some security checks.

```bash
ngrok http 11434 --host-header="localhost:11434"
```

## 4. Get Your Ngrok URL
Copy the `https://....ngrok-free.dev` URL from the terminal output.

## 5. Update Backend Configuration
1. Open `backend/.env`
2. Update `OLLAMA_URL`:
   ```env
   # Example
   OLLAMA_URL=https://your-ngrok-url.ngrok-free.dev
   ```
3. Restart your Backend (`fastapi dev` or redeploy to Vercel).

---

## 💡 Troubleshooting

### "403 Forbidden" or "Access Denied"
- Ensure you used `--host-header="localhost:11434"` in the ngrok command.
- Ensure `OLLAMA_ORIGINS="*"` was set **before** starting `ollama serve`.
- **Note:** The backend code (`Chat_Service.py`) has been patched to automatically send the correct Host header, so API requests should work even if browser visits show 403.

### "Connection Refused"
- Ensure Ollama is actually running (`ollama serve`).
- Ensure it's listening on `0.0.0.0` (not just `127.0.0.1`).
