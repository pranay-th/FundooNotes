import { djangoClient } from './axiosInstances';
import { LOCAL_STORAGE_KEYS } from '@/utils/constants';

/**
 * sendChatMessage — streams the response via SSE.
 */
export async function sendChatMessage(message, history, onToken) {
  const baseURL = djangoClient.defaults.baseURL ?? 'http://localhost:8000';
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
    const lines = buffer.split('\n\n');
    buffer = lines.pop() ?? '';

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith('data:')) continue;
      const data = trimmed.slice('data:'.length).trim();
      if (data === '[DONE]') break;

      try {
        const parsed = JSON.parse(data);
        if (parsed && typeof parsed === 'object' && parsed.error) {
          throw new Error(parsed.error);
        }
        const token = typeof parsed === 'string' ? parsed : '';
        if (token) {
          fullReply += token;
          onToken?.(token);
        }
      } catch (e) {
        if (e.message && !e.message.startsWith('JSON')) throw e;
      }
    }
  }

  return fullReply;
}

/**
 * Fetch smarter proactive suggestions based on note pattern analysis.
 */
export async function getChatSuggestions() {
  const { data } = await djangoClient.get('/api/chatbot/suggestions/');
  return data.payload.suggestions;
}

/**
 * Upload a file (image or text document) for the AI to analyse.
 * Returns { suggested_title, extracted_content, filename }.
 */
export async function analyseFile(file, instruction = '') {
  const formData = new FormData();
  formData.append('file', file);
  if (instruction) formData.append('instruction', instruction);

  const { data } = await djangoClient.post('/api/chatbot/analyse-file/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data.payload;
}
