/**
 * useSpeechRecognition
 *
 * Wraps the browser's Web Speech API (SpeechRecognition / webkitSpeechRecognition).
 * Works in Chrome and Edge; gracefully degrades (isSupported = false) elsewhere.
 *
 * Usage:
 *   const { isSupported, listening, transcript, start, stop, reset } = useSpeechRecognition();
 */
import { useCallback, useEffect, useRef, useState } from 'react';

export function useSpeechRecognition() {
  const SpeechRecognitionAPI =
    typeof window !== 'undefined'
      ? window.SpeechRecognition ?? window.webkitSpeechRecognition
      : undefined;

  const isSupported = Boolean(SpeechRecognitionAPI);

  const recognitionRef = useRef(null);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');

  // Track committed (final) text separately so interim results replace
  // only the trailing partial — not the whole accumulated string.
  const finalRef = useRef('');

  // Build the recognition instance once
  useEffect(() => {
    if (!SpeechRecognitionAPI) return;

    const rec = new SpeechRecognitionAPI();
    rec.continuous = true;        // keep listening until stop() is called
    rec.interimResults = true;    // show live partial results
    rec.lang = 'en-US';

    rec.onresult = (event) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          // Commit this segment permanently
          finalRef.current += result[0].transcript;
        } else {
          // Accumulate interim for display (replaced each tick)
          interim += result[0].transcript;
        }
      }
      // The visible transcript = all committed text + current partial
      setTranscript(finalRef.current + interim);
    };

    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);

    recognitionRef.current = rec;

    return () => {
      rec.abort();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const start = useCallback(() => {
    if (!recognitionRef.current || listening) return;
    finalRef.current = '';
    setTranscript('');
    recognitionRef.current.start();
    setListening(true);
  }, [listening]);

  const stop = useCallback(() => {
    if (!recognitionRef.current || !listening) return;
    recognitionRef.current.stop();
    setListening(false);
  }, [listening]);

  const reset = useCallback(() => {
    finalRef.current = '';
    setTranscript('');
  }, []);

  return { isSupported, listening, transcript, start, stop, reset };
}
