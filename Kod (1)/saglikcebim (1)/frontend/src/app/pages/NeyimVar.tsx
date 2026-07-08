import { useState, useRef, useEffect, useCallback } from "react";
import DOMPurify from "dompurify";
import { Send, Loader2, Bot, User, Mic, MicOff, Stethoscope, PlusCircle, MessageSquare, Volume2, Zap, X } from "lucide-react";
import { apiClient } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";
import ClinicalRoadmapCard from "../../components/ClinicalRoadmapCard";
import { StreamingRoadmapView } from "../../components/StreamingRoadmapView";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function NeyimVar() {
  const { user } = useAuth();
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [roadmapItems, setRoadmapItems] = useState<Record<string, any>>({});
  const [sessions, setSessions] = useState<any[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [chatSuggestions, setChatSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [showStreamingModal, setShowStreamingModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      const data = await apiClient.getChatSessions();
      setSessions(data);
    } catch (e) {
      console.error("Failed to load sessions", e);
    }
  };

  const loadSession = async (sessionId: number) => {
    try {
      setIsLoading(true);
      const data = await apiClient.getChatMessages(sessionId);
      setMessages(data.map((m: any) => ({
        role: m.role,
        content: m.content,
        timestamp: new Date(m.timestamp)
      })));
      setCurrentSessionId(sessionId);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const startNewSession = () => {
    setCurrentSessionId(null);
    setMessages([{
      role: "assistant",
      content: "SİSTEM GÜNCELLENDİ (V2). 🤖 **Özel Chatbot**\n\nLlama 3 Klinik Motoru hazır ve aktif. Bu sistem, tıbbi tahlilleriniz ve şikayetleriniz temelinde klinik yol haritaları oluşturmak için tasarlanmıştır.\n\n📋 Lütfen şu şekilde başlayabilirsiniz:\n• Tahlil sonuçlarınızı paylaşın\n• Sağlık şikayetlerinizi anlatın\n• \"Neyim var?\" sorusunu sorun\n\nSistem, Llama 3 modelini kullanarak size kişiselleştirilmiş analiz ve öneriler sunacaktır.",
      timestamp: new Date()
    }]);
  };

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Initial Greeting
  useEffect(() => {
    if (messages.length === 0 && !currentSessionId) {
      startNewSession();
    }
  }, [messages.length, currentSessionId]);

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'tr-TR';

      let currentTranscript = "";

      recognition.onstart = () => {
         currentTranscript = inputRef.current?.value || "";
      };

      recognition.onresult = (event: any) => {
        let interim = '';
        let final = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            final += event.results[i][0].transcript + ' ';
          } else {
            interim += event.results[i][0].transcript;
          }
        }
        currentTranscript += final;
        setInputValue(currentTranscript + interim);
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        if (event.error === 'not-allowed') {
          alert("Mikrofon izni reddedildi. Lütfen tarayıcı adres çubuğundaki (kilit) ikonuna tıklayıp mikrofona izin verin.");
        }
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
    }
  }, []);

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert("Tarayıcınız sesli yazmayı desteklemiyor. Lütfen Chrome kullanın.");
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      setInputValue("");
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  const sendMessageDirect = async (messageOverride?: string) => {
    const messageText = messageOverride || inputValue.trim();
    if (!messageText || isLoading) return;

    // Force "şikayet" word so the backend NLP engine routes it to DiagnosisAgent
    const backendMessage = messageText; 

    const userMessage: ChatMessage = {
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const history = messages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await apiClient.chatbotChat(backendMessage, history, undefined, currentSessionId || undefined);
      
      setChatSuggestions(response.suggestions || []);

      if (response.session_id && response.session_id !== currentSessionId) {
         setCurrentSessionId(response.session_id);
         fetchSessions(); // Refresh sidebar
      }

      let finalContent = response.answer || "Yanıt alınamadı.";

      // Backend'den gelen hazır HTML'i kullan — JSON kart ayrıca render edilmez
      if (response.type === "clinical_roadmap") {
        finalContent = response.answer;
      }

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: finalContent,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);


    } catch (err) {
      const errorMessage: ChatMessage = {
        role: "assistant",
        content: "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = () => sendMessageDirect();

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMarkdown = (text: string) => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-primary font-semibold">$1</strong>')
      .replace(/\n/g, "<br />");
  };

  const firstName = user?.full_name?.split(" ")[0] || user?.email?.split("@")[0] || "Kullanıcı";

  return (
    <div className="p-4 max-w-[1400px] mx-auto h-[calc(100vh-80px)] flex gap-4">
      {/* Sidebar - Geçmiş Sohbetler */}
      <div className="w-72 bg-card border border-border rounded-2xl shadow-sm flex flex-col hidden md:flex">
        <div className="p-4 border-b border-border flex items-center justify-between">
          <h2 className="font-semibold text-foreground flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-primary" />
            Geçmiş Sohbetler
          </h2>
        </div>
        <div className="p-3">
          <button
            onClick={startNewSession}
            className="w-full flex items-center gap-2 px-3 py-2 bg-primary/10 hover:bg-primary/20 text-primary rounded-xl font-medium transition-colors"
          >
            <PlusCircle className="w-4 h-4" />
            Yeni Sohbet Başlat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-3 pb-3 space-y-1">
          {sessions.map((s) => (
            <button
              key={s.id}
              onClick={() => loadSession(s.id)}
              className={`w-full text-left px-3 py-3 rounded-xl text-sm transition-colors truncate ${
                currentSessionId === s.id
                  ? "bg-primary text-white font-medium shadow-md shadow-primary/20"
                  : "text-muted-foreground hover:bg-surface hover:text-foreground"
              }`}
            >
              {s.title}
            </button>
          ))}
          {sessions.length === 0 && (
            <p className="text-xs text-center text-muted-foreground mt-4">Henüz geçmiş sohbetiniz yok.</p>
          )}
        </div>
      </div>

      {/* Ana Sohbet Ekranı */}
      <div className="flex-1 bg-card border border-border rounded-2xl shadow-sm flex flex-col overflow-hidden relative">
        {/* Header */}
        <div className="absolute top-0 left-0 right-0 p-4 border-b border-border bg-card/80 backdrop-blur-sm z-10 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-sm">
            <Stethoscope className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground leading-tight">SağlıkCebim — Klinik Ön Değerlendirme</h1>
            <p className="text-xs text-muted-foreground">Şikayetlerinizi anlatın, tahlil ve röntgenlerinizle sentezleyelim.</p>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 pt-24 space-y-6">
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  msg.role === "assistant"
                    ? "bg-primary/10 text-primary"
                    : "bg-surface border border-border text-foreground"
                }`}
              >
                {msg.role === "assistant" ? <Bot className="w-5 h-5" /> : <User className="w-5 h-5" />}
              </div>

              <div
                className={`max-w-[75%] rounded-2xl px-5 py-4 text-sm leading-relaxed shadow-sm relative group ${
                  msg.role === "user"
                    ? "bg-primary text-white rounded-tr-sm"
                    : "bg-surface border border-border text-foreground rounded-tl-sm"
                }`}
              >
                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(formatMarkdown(msg.content)) }} />
                <div className="flex items-center justify-between mt-2">
                  <div className={`text-[11px] ${msg.role === "user" ? "text-white/70" : "text-muted-foreground"}`}>
                    {msg.timestamp.toLocaleTimeString("tr-TR", { hour: "2-digit", minute: "2-digit" })}
                  </div>
                  {msg.role === "assistant" && (
                    <button 
                      onClick={() => {
                        if (window.speechSynthesis.speaking) {
                          window.speechSynthesis.cancel();
                        } else {
                          const text = msg.content.replace(/<[^>]*>/g, ''); // HTML'i temizle
                          const utterance = new SpeechSynthesisUtterance(text);
                          utterance.lang = 'tr-TR';
                          window.speechSynthesis.speak(utterance);
                        }
                      }}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-primary/10 rounded transition-all text-primary"
                      title="Sesli Dinle"
                    >
                      <Volume2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
              {/* Roadmap HTML yanıtı zaten content içinde render edilir */}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-primary" />
              </div>
              <div className="bg-surface border border-border rounded-2xl rounded-tl-sm px-5 py-4 flex items-center gap-3">
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
                <span className="text-sm text-muted-foreground">Tüm bulgularınız (Röntgen & Kan) sentezleniyor...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions Bar */}
        {chatSuggestions.length > 0 && !isLoading && (
          <div className="px-6 py-3 border-t border-border bg-surface/50 flex gap-2 overflow-x-auto no-scrollbar">
            {chatSuggestions.map((item) => (
              <button
                key={item}
                onClick={() => {
                  setInputValue(item);
                  // We use a small timeout to let the state update or just call sendMessage with the value
                  // For simplicity, let's just trigger sendMessage logic
                  setTimeout(() => sendMessageDirect(item), 0);
                }}
                className="whitespace-nowrap px-4 py-2 rounded-full bg-primary/10 text-primary text-xs font-medium border border-primary/20 hover:bg-primary hover:text-white transition-all shadow-sm"
              >
                {item}
              </button>
            ))}
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 bg-surface border-t border-border">
          <div className="flex items-end gap-3 max-w-3xl mx-auto relative">
            <textarea
              ref={inputRef as any}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                 if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                 }
              }}
              placeholder={`${firstName}, şu anki şikayetiniz nedir?`}
              className="flex-1 bg-background border border-border rounded-xl px-5 py-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none min-h-[60px] max-h-[120px]"
              disabled={isLoading}
              rows={1}
            />
            
            <div className="absolute right-16 bottom-3 flex gap-2">
              <button                onClick={() => setShowStreamingModal(true)}
                className="p-2 rounded-lg text-muted-foreground hover:bg-card hover:text-primary transition-colors"
                title="Canlı Analiz Modu"
              >
                <Zap className="w-5 h-5" />
              </button>
              <button
                onClick={toggleListening}
                className={`p-2 rounded-lg transition-colors ${
                  isListening 
                  ? "bg-red-500/20 text-red-500 animate-pulse" 
                  : "text-muted-foreground hover:bg-card hover:text-foreground"
                }`}
                title="Sesle Yaz"
              >
                {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
              </button>
            </div>

            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="w-14 h-[60px] bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center disabled:opacity-50 hover:opacity-90 transition-all shadow-md"
            >
              <Send className="w-5 h-5 text-white" />
            </button>
          </div>
        </div>
      </div>

      {/* Streaming Modal */}
      {showStreamingModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-card border border-border rounded-2xl shadow-lg max-w-4xl w-full max-h-[90vh] overflow-auto">
            <div className="sticky top-0 p-4 border-b border-border bg-card flex items-center justify-between">
              <h2 className="font-semibold text-foreground flex items-center gap-2">
                <Zap className="w-5 h-5 text-primary" />
                Canlı Klinik Analiz
              </h2>
              <button
                onClick={() => setShowStreamingModal(false)}
                className="p-1 hover:bg-surface rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-muted-foreground" />
              </button>
            </div>
            <div className="p-6">
              <StreamingRoadmapView
                token={token || undefined}
                onClose={() => setShowStreamingModal(false)}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
