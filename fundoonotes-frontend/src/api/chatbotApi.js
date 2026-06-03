import { djangoClient } from './axiosInstances';

/**
 * Send a message to the AI chatbot and get back the assistant's reply
 * plus the full updated conversation history.
 */
export async function sendChatMessage(message, history) {
  const { data } = await djangoClient.post('/api/chatbot/chat/', { message, history });
  return data.payload;
}

/**
 * Fetch 3 proactive suggestions based on the user's current notes.
 */
export async function getChatSuggestions() {
  const { data } = await djangoClient.get('/api/chatbot/suggestions/');
  return data.payload.suggestions;
}
