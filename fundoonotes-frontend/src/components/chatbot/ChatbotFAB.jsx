import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Avatar,
  Box,
  Chip,
  CircularProgress,
  Collapse,
  Fab,
  IconButton,
  InputAdornment,
  Paper,
  Skeleton,
  TextField,
  Tooltip,
  Typography,
} from '@mui/material';
import { alpha, useTheme as useMuiTheme } from '@mui/material/styles';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CloseIcon from '@mui/icons-material/Close';
import SendRoundedIcon from '@mui/icons-material/SendRounded';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';
import MicIcon from '@mui/icons-material/Mic';
import MicOffIcon from '@mui/icons-material/MicOff';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import { useQueryClient } from '@tanstack/react-query';
import { sendChatMessage, getChatSuggestions } from '@/api/chatbotApi';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { SESSION_STORAGE_KEYS } from '@/utils/constants';

// ── Session-storage helpers ───────────────────────────────────────────────────

function loadFromSession(key, fallback) {
  try {
    const raw = sessionStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function saveToSession(key, value) {
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch { /* quota exceeded — fail silently */ }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function toDisplayMessages(history) {
  return history
    .filter((m) => m.role === 'user' || m.role === 'assistant')
    .filter((m) => typeof m.content === 'string' && m.content.trim() !== '')
    .map((m) => ({
      role: m.role,
      content: m.content,
      timestamp: Date.now(),
    }));
}

// ── Animated thinking dots ────────────────────────────────────────────────────

function ThinkingDots() {
  return (
    <Box sx={{ display: 'flex', gap: '4px', alignItems: 'center', py: 0.5 }}>
      {[0, 1, 2].map((i) => (
        <Box
          key={i}
          sx={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            bgcolor: 'primary.main',
            opacity: 0.7,
            '@keyframes bounce': {
              '0%, 60%, 100%': { transform: 'translateY(0)' },
              '30%': { transform: 'translateY(-6px)' },
            },
            animation: 'bounce 1.2s ease-in-out infinite',
            animationDelay: `${i * 0.2}s`,
          }}
        />
      ))}
    </Box>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function ChatbotFAB() {
  const muiTheme = useMuiTheme();
  const isDark = muiTheme.palette.mode === 'dark';
  const qc = useQueryClient();

  const [open, setOpen] = useState(false);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState(''); // live token buffer
  const [error, setError] = useState(null);

  const [history, setHistory] = useState(() =>
    loadFromSession(SESSION_STORAGE_KEYS.CHAT_HISTORY, []),
  );
  const [displayMessages, setDisplayMessages] = useState(() =>
    loadFromSession(SESSION_STORAGE_KEYS.CHAT_DISPLAY, []),
  );

  useEffect(() => { saveToSession(SESSION_STORAGE_KEYS.CHAT_HISTORY, history); }, [history]);
  useEffect(() => { saveToSession(SESSION_STORAGE_KEYS.CHAT_DISPLAY, displayMessages); }, [displayMessages]);

  const [suggestions, setSuggestions] = useState([]);
  const [suggestionsLoading, setSuggestionsLoading] = useState(false);
  const suggestionsLoaded = useRef(false);

  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  // ── Voice ────────────────────────────────────────────────────────────────
  const { isSupported: voiceSupported, listening, transcript, start: startListening, stop: stopListening, reset: resetTranscript } =
    useSpeechRecognition();

  useEffect(() => { if (transcript) setInput(transcript); }, [transcript]);

  const prevListening = useRef(false);
  useEffect(() => {
    if (prevListening.current && !listening && transcript.trim()) {
      const id = setTimeout(() => {
        handleSendVoice(transcript.trim());
        resetTranscript();
        setInput('');
      }, 400);
      return () => clearTimeout(id);
    }
    prevListening.current = listening;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [listening]);

  // ── Scroll / focus ───────────────────────────────────────────────────────
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [displayMessages, loading]);

  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150);
      if (!suggestionsLoaded.current && displayMessages.length === 0) {
        fetchSuggestions();
        suggestionsLoaded.current = true;
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  // ── Suggestions ──────────────────────────────────────────────────────────
  const fetchSuggestions = async () => {
    setSuggestionsLoading(true);
    try { setSuggestions(await getChatSuggestions()); } catch { /* silent */ }
    finally { setSuggestionsLoading(false); }
  };

  // ── Send ─────────────────────────────────────────────────────────────────
  const _send = useCallback(async (text, fromVoice = false) => {
    if (!text || loading) return;
    setInput('');
    setError(null);
    setSuggestions([]);
    setStreamingContent('');

    const optimistic = { role: 'user', content: text, fromVoice, timestamp: Date.now() };
    setDisplayMessages((prev) => [...prev, optimistic]);
    setLoading(true);

    let fullReply = '';

    try {
      fullReply = await sendChatMessage(text, history, (token) => {
        // Each token arrives here — append to live streaming buffer
        fullReply += token; // local accumulator (sendChatMessage also tracks it)
        setStreamingContent((prev) => prev + token);
      });

      // Streaming done — commit the full reply to the real message list
      const updatedHistory = [
        ...history,
        { role: 'user', content: text },
        { role: 'assistant', content: fullReply },
      ];
      setHistory(updatedHistory);
      setDisplayMessages(toDisplayMessages(updatedHistory));
      setStreamingContent('');

      // Invalidate React Query caches so the UI reflects any changes
      void qc.invalidateQueries({ queryKey: ['notes'] });
      void qc.invalidateQueries({ queryKey: ['labels'] });
      void qc.invalidateQueries({ queryKey: ['shared-notes'] });
      void qc.invalidateQueries({ predicate: (q) => q.queryKey[0] === 'collaborators' });
    } catch (err) {
      setStreamingContent('');
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
      setDisplayMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading, history, qc]);

  const handleSend = useCallback(() => { const t = input.trim(); if (t) _send(t, false); }, [input, _send]);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const handleSendVoice = useCallback((t) => _send(t, true), [_send]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleClear = () => {
    setHistory([]); setDisplayMessages([]); setError(null);
    saveToSession(SESSION_STORAGE_KEYS.CHAT_HISTORY, []);
    saveToSession(SESSION_STORAGE_KEYS.CHAT_DISPLAY, []);
    suggestionsLoaded.current = false;
    setSuggestions([]);
    fetchSuggestions();
    suggestionsLoaded.current = true;
  };

  const handleMicClick = () => {
    if (listening) { stopListening(); }
    else { setInput(''); resetTranscript(); startListening(); }
  };

  const isEmpty = displayMessages.length === 0 && !loading;

  // ── Gradient for the header ───────────────────────────────────────────────
  const headerGradient = isDark
    ? 'linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%)'
    : 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)';

  return (
    <>
      {/* ── FAB with gradient glow ─────────────────────────────────────── */}
      <Tooltip title="AI Assistant" placement="left">
        <Fab
          aria-label="Open AI assistant"
          onClick={() => setOpen((v) => !v)}
          sx={{
            position: 'fixed',
            bottom: 28,
            right: 28,
            zIndex: 1300,
            background: open
              ? (isDark ? '#2d2e30' : '#f8f9fa')
              : 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)',
            color: open ? 'text.primary' : '#fff',
            boxShadow: open
              ? 2
              : '0 4px 20px rgba(26,115,232,0.45), 0 2px 8px rgba(124,58,237,0.3)',
            '&:hover': {
              background: open
                ? (isDark ? '#3a3b3c' : '#e8eaed')
                : 'linear-gradient(135deg, #1c7fe8 0%, #8b44f0 100%)',
              transform: 'scale(1.05)',
            },
            transition: 'transform 0.15s ease, box-shadow 0.15s ease',
          }}
        >
          {open ? <CloseIcon /> : <AutoAwesomeIcon />}
        </Fab>
      </Tooltip>

      {/* ── Panel ──────────────────────────────────────────────────────── */}
      <Collapse
        in={open}
        timeout={220}
        sx={{
          position: 'fixed',
          bottom: 88,
          right: 28,
          zIndex: 1300,
          width: { xs: 'calc(100vw - 40px)', sm: 420 },
          transformOrigin: 'bottom right',
        }}
      >
        <Paper
          elevation={0}
          sx={{
            display: 'flex',
            flexDirection: 'column',
            height: 580,
            borderRadius: 4,
            overflow: 'hidden',
            border: '1px solid',
            borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.08)',
            boxShadow: isDark
              ? '0 32px 80px rgba(0,0,0,0.5), 0 8px 24px rgba(0,0,0,0.3)'
              : '0 32px 80px rgba(0,0,0,0.14), 0 8px 24px rgba(0,0,0,0.06)',
          }}
        >
          {/* ── Gradient header ─────────────────────────────────────── */}
          <Box
            sx={{
              px: 2,
              py: 1.5,
              background: headerGradient,
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              flexShrink: 0,
            }}
          >
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: 2,
                bgcolor: 'rgba(255,255,255,0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backdropFilter: 'blur(8px)',
              }}
            >
              <SmartToyIcon sx={{ fontSize: 18, color: '#fff' }} />
            </Box>
            <Box flex={1}>
              <Typography variant="subtitle2" fontWeight={700} sx={{ color: '#fff', lineHeight: 1.2 }}>
                FundooNotes AI
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', fontSize: 11 }}>
                {loading ? 'Thinking…' : 'Ask me anything'}
              </Typography>
            </Box>
            <Tooltip title="Clear conversation">
              <IconButton
                size="small"
                onClick={handleClear}
                sx={{ color: 'rgba(255,255,255,0.8)', '&:hover': { bgcolor: 'rgba(255,255,255,0.15)' } }}
                aria-label="Clear conversation"
              >
                <DeleteSweepIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>

          {/* ── Messages area ───────────────────────────────────────── */}
          <Box
            sx={{
              flex: 1,
              overflowY: 'auto',
              px: 2,
              py: 2,
              display: 'flex',
              flexDirection: 'column',
              gap: 1.5,
              bgcolor: isDark ? 'rgba(255,255,255,0.02)' : 'rgba(0,0,0,0.015)',
            }}
          >
            {isEmpty && (
              <Box
                sx={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 2,
                  textAlign: 'center',
                  px: 2,
                }}
              >
                <Box
                  sx={{
                    width: 64,
                    height: 64,
                    borderRadius: 4,
                    background: 'linear-gradient(135deg, rgba(26,115,232,0.15) 0%, rgba(124,58,237,0.15) 100%)',
                    border: '1px solid',
                    borderColor: isDark ? 'rgba(138,180,248,0.2)' : 'rgba(26,115,232,0.2)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <AutoAwesomeIcon sx={{ fontSize: 32, color: 'primary.main', opacity: 0.8 }} />
                </Box>
                <Box>
                  <Typography variant="body2" fontWeight={500}>
                    What can I help you with?
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.25 }}>
                    {voiceSupported ? 'Type or tap the mic to speak.' : 'Type a command below.'}
                  </Typography>
                </Box>

                {/* Suggestions */}
                <Box sx={{ width: '100%' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1.25, justifyContent: 'center' }}>
                    <TipsAndUpdatesIcon sx={{ fontSize: 13, color: 'primary.main' }} />
                    <Typography variant="caption" fontWeight={600} color="primary.main">
                      Suggested for you
                    </Typography>
                  </Box>
                  {suggestionsLoading ? (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                      {[1, 2, 3].map((i) => (
                        <Skeleton key={i} variant="rounded" height={34} sx={{ borderRadius: 2.5 }} />
                      ))}
                    </Box>
                  ) : (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                      {suggestions.map((s, i) => (
                        <Chip
                          key={i}
                          label={s}
                          size="small"
                          onClick={() => _send(s, false)}
                          clickable
                          sx={{
                            height: 'auto',
                            py: 0.75,
                            borderRadius: 2.5,
                            border: '1px solid',
                            borderColor: isDark ? 'rgba(138,180,248,0.2)' : 'rgba(26,115,232,0.15)',
                            bgcolor: isDark ? 'rgba(138,180,248,0.05)' : 'rgba(26,115,232,0.04)',
                            '&:hover': {
                              bgcolor: isDark ? 'rgba(138,180,248,0.12)' : 'rgba(26,115,232,0.1)',
                              borderColor: 'primary.main',
                            },
                            '& .MuiChip-label': { whiteSpace: 'normal', textAlign: 'left', fontSize: '0.73rem', lineHeight: 1.4 },
                          }}
                        />
                      ))}
                    </Box>
                  )}
                </Box>
              </Box>
            )}

            {displayMessages.map((msg, i) => (
              <MessageBubble key={i} message={msg} isDark={isDark} />
            ))}

            {loading && (
              <Box sx={{ display: 'flex', alignItems: 'flex-end', gap: 1 }}>
                <Avatar sx={{ width: 28, height: 28, background: headerGradient }}>
                  <SmartToyIcon sx={{ fontSize: 15 }} />
                </Avatar>
                <Paper
                  elevation={0}
                  sx={{
                    px: 1.75,
                    py: 1,
                    borderRadius: 2.5,
                    borderBottomLeftRadius: 0,
                    bgcolor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
                    border: '1px solid',
                    borderColor: 'divider',
                    maxWidth: '78%',
                  }}
                >
                  {streamingContent ? (
                    // Tokens are arriving — render them live with a blinking cursor
                    <Typography
                      variant="body2"
                      sx={{ lineHeight: 1.55, fontSize: '0.855rem', whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
                    >
                      {streamingContent}
                      <Box
                        component="span"
                        sx={{
                          display: 'inline-block',
                          width: '2px',
                          height: '1em',
                          bgcolor: 'primary.main',
                          ml: '2px',
                          verticalAlign: 'text-bottom',
                          '@keyframes blink': {
                            '0%, 100%': { opacity: 1 },
                            '50%': { opacity: 0 },
                          },
                          animation: 'blink 0.8s ease-in-out infinite',
                        }}
                      />
                    </Typography>
                  ) : (
                    // Waiting for first token — show the animated dots
                    <ThinkingDots />
                  )}
                </Paper>
              </Box>
            )}

            {error && (
              <Box
                sx={{
                  mx: 'auto',
                  px: 1.5,
                  py: 0.75,
                  borderRadius: 2,
                  bgcolor: 'rgba(211,47,47,0.08)',
                  border: '1px solid rgba(211,47,47,0.2)',
                }}
              >
                <Typography variant="caption" color="error">{error}</Typography>
              </Box>
            )}

            <div ref={bottomRef} />
          </Box>

          {/* ── Voice listening banner ──────────────────────────────── */}
          <Collapse in={listening}>
            <Box
              sx={{
                px: 2,
                py: 0.875,
                background: 'linear-gradient(90deg, #d32f2f 0%, #c62828 100%)',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                gap: 1.5,
              }}
            >
              <Box
                sx={{
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  bgcolor: '#fff',
                  flexShrink: 0,
                  '@keyframes recPulse': {
                    '0%, 100%': { opacity: 1, transform: 'scale(1)' },
                    '50%': { opacity: 0.4, transform: 'scale(0.8)' },
                  },
                  animation: 'recPulse 1s ease-in-out infinite',
                }}
              />
              <Typography variant="caption" flex={1} fontWeight={500}>
                Listening — speak your command
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.75 }}>Tap mic to stop</Typography>
            </Box>
          </Collapse>

          {/* ── Input ───────────────────────────────────────────────── */}
          <Box
            sx={{
              px: 1.5,
              py: 1.25,
              borderTop: '1px solid',
              borderColor: 'divider',
              bgcolor: 'background.paper',
              display: 'flex',
              alignItems: 'flex-end',
              gap: 0.75,
            }}
          >
            {voiceSupported && (
              <Tooltip title={listening ? 'Stop' : 'Speak'}>
                <IconButton
                  size="small"
                  onClick={handleMicClick}
                  sx={{
                    mb: 0.25,
                    color: listening ? 'error.main' : 'text.secondary',
                    bgcolor: listening ? alpha(muiTheme.palette.error.main, 0.08) : 'transparent',
                    border: '1px solid',
                    borderColor: listening ? 'error.light' : 'divider',
                    '&:hover': { bgcolor: listening ? alpha(muiTheme.palette.error.main, 0.14) : 'action.hover' },
                    ...(listening && {
                      '@keyframes micGrow': {
                        '0%, 100%': { transform: 'scale(1)' },
                        '50%': { transform: 'scale(1.15)' },
                      },
                      animation: 'micGrow 1s ease-in-out infinite',
                    }),
                  }}
                  aria-label={listening ? 'Stop voice input' : 'Start voice input'}
                >
                  {listening ? <MicIcon sx={{ fontSize: 18 }} /> : <MicOffIcon sx={{ fontSize: 18 }} />}
                </IconButton>
              </Tooltip>
            )}

            <TextField
              inputRef={inputRef}
              fullWidth
              size="small"
              placeholder={listening ? 'Listening…' : 'Message FundooNotes AI…'}
              multiline
              maxRows={4}
              value={input}
              onChange={(e) => {
                if (!listening) setInput(e.target.value);
              }}
              onKeyDown={handleKeyDown}
              disabled={loading}
              inputProps={{ readOnly: listening }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  bgcolor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
                  '& fieldset': { borderColor: 'divider' },
                  '&:hover fieldset': { borderColor: 'primary.light' },
                  '&.Mui-focused fieldset': { borderColor: 'primary.main' },
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton
                      size="small"
                      onClick={handleSend}
                      disabled={!input.trim() || loading}
                      sx={{
                        color: '#fff',
                        background: !input.trim() || loading || listening
                          ? 'rgba(0,0,0,0.12)'
                          : 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)',
                        borderRadius: 2,
                        p: 0.75,
                        '&:hover:not(:disabled)': {
                          background: 'linear-gradient(135deg, #1c7fe8 0%, #8b44f0 100%)',
                          transform: 'scale(1.05)',
                        },
                        transition: 'transform 0.12s ease',
                      }}
                      aria-label="Send message"
                    >
                      <SendRoundedIcon sx={{ fontSize: 16 }} />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
          </Box>
        </Paper>
      </Collapse>
    </>
  );
}

// ── Message bubble ────────────────────────────────────────────────────────────

function MessageBubble({ message, isDark }) {
  const isUser = message.role === 'user';
  const headerGradient = isDark
    ? 'linear-gradient(135deg, #1e3a5f 0%, #2d1b4e 100%)'
    : 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)';

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-end',
        gap: 1,
      }}
    >
      {/* Avatar */}
      <Avatar
        sx={{
          width: 28,
          height: 28,
          background: isUser
            ? (isDark ? 'rgba(138,180,248,0.2)' : 'rgba(26,115,232,0.12)')
            : headerGradient,
          flexShrink: 0,
          border: '1px solid',
          borderColor: isUser
            ? (isDark ? 'rgba(138,180,248,0.3)' : 'rgba(26,115,232,0.2)')
            : 'transparent',
        }}
      >
        {isUser ? (
          <PersonIcon sx={{ fontSize: 15, color: 'primary.main' }} />
        ) : (
          <SmartToyIcon sx={{ fontSize: 15, color: '#fff' }} />
        )}
      </Avatar>

      {/* Bubble */}
      <Paper
        elevation={0}
        sx={{
          px: 1.75,
          py: 1,
          maxWidth: '78%',
          borderRadius: 2.5,
          borderBottomRightRadius: isUser ? 4 : 2.5,
          borderBottomLeftRadius: isUser ? 2.5 : 4,
          background: isUser
            ? 'linear-gradient(135deg, #1a73e8 0%, #7c3aed 100%)'
            : (isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)'),
          color: isUser ? '#fff' : 'text.primary',
          wordBreak: 'break-word',
          whiteSpace: 'pre-wrap',
          border: isUser ? 'none' : '1px solid',
          borderColor: isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
          position: 'relative',
        }}
      >
        <Typography variant="body2" sx={{ lineHeight: 1.55, fontSize: '0.855rem' }}>
          {message.content}
        </Typography>
        {message.fromVoice && (
          <Tooltip title="Sent by voice">
            <MicIcon
              sx={{
                fontSize: 10,
                position: 'absolute',
                bottom: 4,
                right: isUser ? 5 : 'auto',
                left: isUser ? 'auto' : 5,
                opacity: 0.5,
                color: isUser ? '#fff' : 'text.secondary',
              }}
            />
          </Tooltip>
        )}
      </Paper>
    </Box>
  );
}
