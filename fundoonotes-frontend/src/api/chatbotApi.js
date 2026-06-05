import { djangoClient } from './axiosInstances';
import { LOCAL_STORAGE_KEYS } from '@/utils/constants';

/**
 * sendChatMessage
 *
 * Sends a message and streams the response via SSE.
 *
 * @param {string}   message   - The user's message
 * @param {Array}    history   - Prior [{role, content}] pairs
 * @param {Function} onToken   - Called with each streamed token string
 * @returns {Promise<string>}  - Resolves with the full reply once streaming ends
 */
export async function sendChatMessage(message, history, onToken) {
  const baseURL =
    djangoClient.defaults.baseURL ?? 'http://localhost:8000';

  // We need the raw fetch API for SSE — axios does not support streaming
  const accessToken = localStorage.getItem(LOCAL_STORAGE_KEYS.ACCESS_TOKEN);

  const response = await fetch(`${baseURL}/api/chatbot/chat/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(errText || `HTTP ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullReply = '';
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSE lines are separated by \n\n
    const lines = buffer.split('\n\n');
    // Keep the last incomplete chunk in the buffer
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith('data:')) continue;

      const data = trimmed.slice('data:'.length).trim();
      if (data === '[DONE]') break;

      try {
        const parsed = JSON.parse(data);
        // Error event from backend: { error: "..." }
        if (parsed && typeof parsed === 'object' && parsed.error) {
          throw new Error(parsed.error);
        }
        // Normal token — parsed is a plain string
        const token = typeof parsed === 'string' ? parsed : '';
        if (token) {
          fullReply += token;
          onToken?.(token);
        }
      } catch (e) {
        // Re-throw error events; ignore malformed chunks
        if (e.message && !e.message.startsWith('JSON')) throw e;
      }
    }
  }

  return fullReply;
}

/**
 * Fetch 3 proactive suggestions based on the user's current notes.
 */
export async function getChatSuggestions() {
  const { data } = await djangoClient.get('/api/chatbot/suggestions/');
  return data.payload.suggestions;
}
