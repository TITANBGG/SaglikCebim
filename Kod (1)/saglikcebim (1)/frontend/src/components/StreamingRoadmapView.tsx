import React, { useState } from 'react';
import { Loader, AlertCircle } from 'lucide-react';
import { ClinicalRoadmapCard } from './ClinicalRoadmapCard';
import { useStreamingRoadmap } from '../hooks/useStreamingRoadmap';

interface StreamingRoadmapViewProps {
  token?: string;
  onClose?: () => void;
}

export function StreamingRoadmapView({ token, onClose }: StreamingRoadmapViewProps) {
  const [inputMessage, setInputMessage] = useState('');
  const { state, generate, reset } = useStreamingRoadmap();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputMessage.trim() || state.isStreaming) return;
    generate(inputMessage, token);
  };

  const handleNewAnalysis = () => {
    reset();
    setInputMessage('');
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4 space-y-4">
      {/* Input Form */}
      {!state.isDone && (
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Semptomlarınızı ve şikayetlerinizi detaylı olarak yazın (örn: 3 gündür boğaz ağrısı ve istemsiz gırtlak kasılması)..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={4}
            disabled={state.isStreaming}
          />
          <button
            type="submit"
            disabled={state.isStreaming || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {state.isStreaming ? (
              <span className="flex items-center gap-2">
                <Loader className="w-4 h-4 animate-spin" />
                Analiz Yapılıyor...
              </span>
            ) : (
              'Analiz Başlat'
            )}
          </button>
        </form>
      )}

      {/* Status Messages */}
      {state.isStreaming && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-700">
          <div className="flex items-center gap-2">
            <Loader className="w-4 h-4 animate-spin" />
            <span>
              {state.message || `${state.step} aşamasında...`}
            </span>
          </div>
        </div>
      )}

      {/* Token Preview (While Streaming) */}
      {state.isStreaming && state.tokens && (
        <div className="p-3 bg-gray-50 border border-gray-300 rounded-lg max-h-48 overflow-y-auto">
          <div className="text-xs text-gray-600 mb-2">Canlı İşlem Akışı:</div>
          <pre className="text-xs font-mono text-gray-700 whitespace-pre-wrap break-words">
            {state.tokens}
          </pre>
        </div>
      )}

      {/* Follow-up Question */}
      {state.followupQuestion && (
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
          <strong>Takip Sorusu:</strong> {state.followupQuestion}
        </div>
      )}

      {/* Safety Warnings */}
      {state.safetyWarnings.length > 0 && (
        <div className="p-3 bg-orange-50 border border-orange-300 rounded-lg">
          <div className="flex gap-2 items-start">
            <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-orange-800">
              <strong>Güvenlik Uyarıları:</strong>
              <ul className="list-disc ml-5 mt-2">
                {state.safetyWarnings.map((warning, idx) => (
                  <li key={idx}>{warning}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {state.error && (
        <div className="p-3 bg-red-50 border border-red-300 rounded-lg text-sm text-red-800 flex gap-2 items-start">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <strong>Hata:</strong> {state.error}
          </div>
        </div>
      )}

      {/* Final Roadmap */}
      {state.roadmap && (
        <div className="border border-green-200 bg-green-50 rounded-lg p-4">
          <ClinicalRoadmapCard roadmap={state.roadmap} />
          
          {/* Action Buttons */}
          <div className="flex gap-2 mt-4">
            <button
              onClick={handleNewAnalysis}
              className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium"
            >
              Yeni Analiz
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="flex-1 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 font-medium"
              >
                Kapat
              </button>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!state.isStreaming && !state.isDone && !state.error && (
        <div className="text-center p-8 text-gray-500">
          <p>Semptomlarınızı yazarak klinik analiz başlatın</p>
        </div>
      )}
    </div>
  );
}
