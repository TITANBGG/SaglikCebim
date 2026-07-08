import { useState, useRef, useEffect, useCallback } from "react";
import DOMPurify from "dompurify";
import {
  MessageCircle,
  X,
  Send,
  Loader2,
  Bot,
  User,
  Sparkles,
  ExternalLink,
  ChevronDown,
  Mic,
  MicOff
} from "lucide-react";
import { apiClient } from "../../api/client";
import { useAuth } from "../../contexts/AuthContext";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  msgType?: "clinical_roadmap" | "chat_message";
  articles?: Array<{
    pmid: string;
    title: string;
    authors: string;
    journal: string;
    year: string;
    url: string;
    abstract: string;
  }>;
  suggestions?: string[];
  timestamp: Date;
}

interface HealthChatBotProps {
  reportId?: string;
}

export function HealthChatBot({ reportId }: HealthChatBotProps) {
  const { user } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showArticles, setShowArticles] = useState<string | null>(null);
  const [isListening, setIsListening] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // SpeechRecognition Setup
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'tr-TR';

      let currentTranscript = "";

      recognition.onstart = () => {
         // Başladığında o anki input değerini hafızaya al
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

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // İlk açılışta karşılama mesajı
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      sendMessage("merhaba");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const sendMessage = async (text?: string) => {
    const messageText = text || inputValue.trim();
    if (!messageText || isLoading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: messageText,
      timestamp: new Date(),
    };

    // Greeting mesajını kullanıcıya gösterme
    if (!text) {
      setMessages((prev) => [...prev, userMessage]);
    }
    setInputValue("");
    setIsLoading(true);

    try {
      const history = messages.slice(-12).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await apiClient.chatbotChat(
        messageText,
        history,
        reportId
      );

      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: response.answer || "Yanıt alınamadı.",
        msgType: response.type,
        articles: response.pubmed_articles || response.articles || [],
        suggestions: response.suggestions || [],
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage: ChatMessage = {
        role: "assistant",
        content:
          "Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin. Backend bağlantısını kontrol edin.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    const userMsg: ChatMessage = {
      role: "user",
      content: suggestion,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    apiClient
      .chatbotChat(
        suggestion,
        messages.slice(-12).map((m) => ({ role: m.role, content: m.content })),
        reportId
      )
      .then((response) => {
        const assistantMessage: ChatMessage = {
          role: "assistant",
          content: response.answer || "Yanıt alınamadı.",
          msgType: response.type,
          articles: response.pubmed_articles || response.articles || [],
          suggestions: response.suggestions || [],
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      })
      .catch(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant" as const,
            content: "Bir hata oluştu, lütfen tekrar deneyin.",
            timestamp: new Date(),
          },
        ]);
      })
      .finally(() => {
        setIsLoading(false);
        setInputValue("");
      });
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMarkdown = (text: string) => {
    // Basit markdown: **bold**, \n => <br>
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-primary font-semibold">$1</strong>')
      .replace(/\n/g, "<br />");
  };

  const firstName = user?.full_name?.split(" ")[0] || user?.email?.split("@")[0] || "Kullanıcı";

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          id="chatbot-toggle-btn"
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 group"
          style={{ filter: "drop-shadow(0 8px 24px rgba(45, 212, 255, 0.35))" }}
        >
          <div className="relative w-16 h-16 bg-gradient-to-br from-primary via-accent to-primary rounded-2xl flex items-center justify-center transition-all duration-300 group-hover:scale-110 group-hover:rounded-xl">
            {/* Pulse animation */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary to-accent rounded-2xl animate-ping opacity-20" />
            <MessageCircle className="w-7 h-7 text-white relative z-10" />
          </div>
          {/* Tooltip */}
          <div className="absolute bottom-full right-0 mb-3 px-4 py-2 bg-card border border-border rounded-xl text-sm text-foreground whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity shadow-lg">
            <Sparkles className="w-3.5 h-3.5 inline mr-1.5 text-primary" />
            Sağlık Asistanı
            <div className="absolute top-full right-6 w-2 h-2 bg-card border-b border-r border-border rotate-45 -mt-1" />
          </div>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div
          className="fixed bottom-6 right-6 z-50 w-[calc(100vw-2rem)] max-w-[420px] h-[620px] flex flex-col bg-card border border-border rounded-2xl overflow-hidden"
          style={{
            boxShadow: "0 25px 60px rgba(0,0,0,0.5), 0 0 40px rgba(45, 212, 255, 0.1)",
            animation: "chatSlideUp 0.3s ease-out",
          }}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 bg-gradient-to-r from-primary/15 via-accent/10 to-transparent border-b border-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-foreground">Sağlık Asistanı</h3>
                <p className="text-xs text-muted-foreground">Kişiye özel sağlık tavsiyeleri</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="w-8 h-8 rounded-lg hover:bg-destructive/10 flex items-center justify-center transition-colors"
            >
              <X className="w-4 h-4 text-muted-foreground hover:text-destructive" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-thin">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex gap-2.5 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                {/* Avatar */}
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    msg.role === "assistant"
                      ? "bg-gradient-to-br from-primary/20 to-accent/20"
                      : "bg-primary/10"
                  }`}
                >
                  {msg.role === "assistant" ? (
                    <Bot className="w-4 h-4 text-primary" />
                  ) : (
                    <User className="w-4 h-4 text-primary" />
                  )}
                </div>

                {/* Message Bubble */}
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.role === "user"
                      ? "bg-primary text-white rounded-br-md"
                      : "bg-surface border border-border text-foreground rounded-bl-md"
                  }`}
                >
                  {msg.msgType === "clinical_roadmap"
                    ? <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(msg.content) }} />
                    : <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(formatMarkdown(msg.content)) }} />
                  }

                  {/* PubMed Articles */}
                  {msg.articles && msg.articles.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-border/40">
                      <button
                        onClick={() =>
                          setShowArticles(showArticles === `msg-${idx}` ? null : `msg-${idx}`)
                        }
                        className="flex items-center gap-1.5 text-xs text-primary hover:text-primary/80 transition-colors"
                      >
                        <Sparkles className="w-3 h-3" />
                        <span>{msg.articles.length} PubMed Makalesi</span>
                        <ChevronDown
                          className={`w-3 h-3 transition-transform ${
                            showArticles === `msg-${idx}` ? "rotate-180" : ""
                          }`}
                        />
                      </button>
                      {showArticles === `msg-${idx}` && (
                        <div className="mt-2 space-y-2">
                          {msg.articles.map((article, aIdx) => (
                            <a
                              key={aIdx}
                              href={article.url}
                              target="_blank"
                              rel="noreferrer"
                              className="block p-2.5 bg-background/50 border border-border/50 rounded-lg hover:border-primary/40 transition-all"
                            >
                              <p className="text-xs font-semibold text-foreground line-clamp-2 mb-1">
                                {article.title}
                              </p>
                              {article.summary && (
                                <p className="text-[10px] text-muted-foreground line-clamp-2 mb-1">
                                  {article.summary}
                                </p>
                              )}
                              <div className="flex items-center gap-2 mt-1 text-[10px] text-primary">
                                <ExternalLink className="w-2.5 h-2.5" />
                                <span>PubMed {article.pmid ? `· PMID ${article.pmid}` : ""}</span>
                                {article.year && <span>· {article.year}</span>}
                                {article.evidence_level && <span>· {article.evidence_level}</span>}
                              </div>
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Suggestions */}
                  {msg.role === "assistant" &&
                    msg.suggestions &&
                    msg.suggestions.length > 0 &&
                    idx === messages.length - 1 && (
                      <div className="mt-3 pt-3 border-t border-border/40 flex flex-wrap gap-1.5">
                        {msg.suggestions.map((sug, sIdx) => (
                          <button
                            key={sIdx}
                            onClick={() => handleSuggestionClick(sug)}
                            className="px-3 py-1.5 text-[11px] bg-primary/10 text-primary border border-primary/20 rounded-full hover:bg-primary/20 transition-colors whitespace-nowrap"
                          >
                            {sug}
                          </button>
                        ))}
                      </div>
                    )}

                  {/* Timestamp */}
                  <div
                    className={`text-[10px] mt-1.5 ${
                      msg.role === "user" ? "text-white/60" : "text-muted-foreground"
                    }`}
                  >
                    {msg.timestamp.toLocaleTimeString("tr-TR", {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div className="bg-surface border border-border rounded-2xl rounded-bl-md px-4 py-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 text-primary animate-spin" />
                    <span className="text-sm text-muted-foreground">Yanıt hazırlanıyor...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="px-4 py-3 border-t border-border bg-surface/50">
            <div className="flex items-center gap-2">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder={`${firstName}, bir soru sorun...`}
                className="flex-1 bg-background border border-border rounded-xl px-4 py-2.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                disabled={isLoading}
              />
              <button
                onClick={toggleListening}
                className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
                  isListening 
                  ? "bg-red-500/20 text-red-500 hover:bg-red-500/30 animate-pulse" 
                  : "bg-surface border border-border text-muted-foreground hover:text-foreground"
                }`}
                title={isListening ? "Dinlemeyi Durdur" : "Sesle Yaz"}
              >
                {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </button>
              <button
                onClick={() => sendMessage()}
                disabled={!inputValue.trim() || isLoading}
                className="w-10 h-10 bg-gradient-to-br from-primary to-accent rounded-xl flex items-center justify-center disabled:opacity-40 hover:opacity-90 transition-all"
              >
                <Send className="w-4 h-4 text-white" />
              </button>
            </div>
            <p className="text-[10px] text-muted-foreground text-center mt-2">
              ⚠️ Bu asistan bilgilendirme amaçlıdır, tıbbi tanı yerine geçmez.
            </p>
          </div>
        </div>
      )}

      {/* CSS Animation */}
      <style>{`
        @keyframes chatSlideUp {
          from {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
        .scrollbar-thin::-webkit-scrollbar {
          width: 4px;
        }
        .scrollbar-thin::-webkit-scrollbar-track {
          background: transparent;
        }
        .scrollbar-thin::-webkit-scrollbar-thumb {
          background: hsl(var(--border));
          border-radius: 4px;
        }
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      `}</style>
    </>
  );
}
