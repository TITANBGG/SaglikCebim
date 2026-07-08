import { useState, useCallback } from 'react';
import { ClinicalRoadmap } from '../types/roadmap';

interface StreamState {
  status: 'idle' | 'streaming' | 'done' | 'error';
  step: string;
  message: string;
  tokens: string;
  followupQuestion: string | null;
  safetyWarnings: string[];
  roadmap: ClinicalRoadmap | null;
  error: string | null;
  isStreaming: boolean;
  isDone: boolean;
}

export function useStreamingRoadmap() {
  const [state, setState] = useState<StreamState>({
    status: 'idle',
    step: '',
    message: '',
    tokens: '',
    followupQuestion: null,
    safetyWarnings: [],
    roadmap: null,
    error: null,
    isStreaming: false,
    isDone: false,
  });

  const generate = useCallback(
    async (message: string, token?: string) => {
      setState((s) => ({
        ...s,
        status: 'streaming',
        isStreaming: true,
        isDone: false,
        tokens: '',
        roadmap: null,
        error: null,
        safetyWarnings: [],
        followupQuestion: null,
      }));

      try {
        const authHeader = token ? `Bearer ${token}` : '';
        const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

        const response = await fetch(`${apiUrl}/api/v1/roadmap/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(authHeader && { Authorization: authHeader }),
          },
          body: JSON.stringify({ message, use_evidence: true }),
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        if (!response.body) {
          throw new Error('No response body');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let eventBuffer = '';

        // eslint-disable-next-line no-constant-condition
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          eventBuffer += decoder.decode(value, { stream: true });

          // Parse SSE format (event: type\ndata: JSON\n\n)
          const events = eventBuffer.split('\n\n');
          eventBuffer = events.pop() || ''; // Keep incomplete event

          for (const eventStr of events) {
            if (!eventStr.trim()) continue;

            const lines = eventStr.split('\n');
            let eventType = '';
            let eventData = '';

            for (const line of lines) {
              if (line.startsWith('event: ')) {
                eventType = line.substring(7);
              } else if (line.startsWith('data: ')) {
                eventData = line.substring(6);
              }
            }

            if (!eventType || !eventData) continue;

            try {
              const data = JSON.parse(eventData);

              setState((prevState) => {
                const newState = { ...prevState };

                switch (eventType) {
                  case 'status':
                    newState.step = data.step || '';
                    newState.message = data.message || '';
                    break;

                  case 'token':
                    newState.tokens += data.content || '';
                    break;

                  case 'followupQuestion':
                    newState.followupQuestion = data.question || null;
                    break;

                  case 'safety_warning':
                    newState.safetyWarnings = data.violations || [];
                    break;

                  case 'roadmap':
                    newState.roadmap = data as ClinicalRoadmap;
                    newState.tokens = ''; // Clear tokens when roadmap arrives
                    break;

                  case 'done':
                    newState.status = data.status === 'success' ? 'done' : 'error';
                    newState.isStreaming = false;
                    newState.isDone = true;
                    break;

                  case 'error':
                    newState.status = 'error';
                    newState.error = data.message || 'Unknown error';
                    newState.isStreaming = false;
                    newState.isDone = true;
                    break;

                  default:
                    break;
                }

                return newState;
              });
            } catch (parseErr) {
              console.error('[useStreamingRoadmap] JSON parse error:', parseErr);
            }
          }
        }

        // Final flush of buffer if needed
        if (eventBuffer.trim()) {
          const lines = eventBuffer.split('\n');
          let eventType = '';
          let eventData = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) {
              eventType = line.substring(7);
            } else if (line.startsWith('data: ')) {
              eventData = line.substring(6);
            }
          }

          if (eventType && eventData) {
            const data = JSON.parse(eventData);
            setState((prevState) => {
              const newState = { ...prevState };

              switch (eventType) {
                case 'roadmap':
                  newState.roadmap = data as ClinicalRoadmap;
                  newState.tokens = '';
                  break;

                case 'done':
                  newState.status = 'done';
                  newState.isStreaming = false;
                  newState.isDone = true;
                  break;

                default:
                  break;
              }

              return newState;
            });
          }
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        setState((s) => ({
          ...s,
          status: 'error',
          error: errorMsg,
          isStreaming: false,
          isDone: true,
        }));
      }
    },
    []
  );

  const reset = useCallback(() => {
    setState({
      status: 'idle',
      step: '',
      message: '',
      tokens: '',
      followupQuestion: null,
      safetyWarnings: [],
      roadmap: null,
      error: null,
      isStreaming: false,
      isDone: false,
    });
  }, []);

  return {
    state,
    generate,
    reset,
  };
}
