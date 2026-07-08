import { useEffect, useState } from "react";
import DOMPurify from "dompurify";
import { BookOpen, Calendar, Clock, ExternalLink, Loader2, MessageCircle, Search } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { TopBar } from "../components/TopBar";
import { apiClient } from "../../api/client";

export function Makaleler() {
  const [dailyArticles, setDailyArticles] = useState<any[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [chatMessage, setChatMessage] = useState("");
  const [chatAnswer, setChatAnswer] = useState("");
  const [chatSuggestions, setChatSuggestions] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDaily = async () => {
      try {
        const response = await apiClient.getDailyArticles();
        setDailyArticles(response.articles || []);
      } catch (err) {
        console.error(err);
      }
    };

    loadDaily();
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    try {
      setIsSearching(true);
      setError("");
      const response = await apiClient.searchArticles(searchQuery, 10);
      setSearchResults(response.articles || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Makaleler aranamadı");
    } finally {
      setIsSearching(false);
    }
  };

  const handleChatDirect = async (messageOverride?: string) => {
    const messageToSend = messageOverride || chatMessage;
    if (!messageToSend.trim()) return;
    
    try {
      setIsChatting(true);
      setError("");
      // 'Neyim Var?' motoruna (chatbotChat) bağlıyoruz
      const response = await apiClient.chatbotChat(messageToSend, [], undefined, undefined);
      setChatAnswer(response.answer || "");
      setChatSuggestions(response.suggestions || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Sohbet çalışmadı");
    } finally {
      setIsChatting(false);
    }
  };

  const handleChat = () => handleChatDirect();

  const renderArticleCard = (article: any) => (
    <a
      key={article.pmid}
      href={article.url}
      target="_blank"
      rel="noreferrer"
      className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)] hover:bg-card-hover hover:border-border-strong transition-all cursor-pointer group block"
    >
      <div className="flex items-start justify-between mb-4">
        <Badge className="bg-primary/10 text-primary border-primary/20">PubMed</Badge>
        <div className="flex items-center gap-2 text-muted-foreground text-sm">
          <Clock className="w-4 h-4" />
          <span>{article.pub_date || ""}</span>
        </div>
      </div>

      <h3 className="text-xl font-bold text-foreground mb-3 group-hover:text-primary transition-colors">{article.title}</h3>
      <p className="text-muted-foreground mb-4 leading-relaxed line-clamp-3">{article.abstract}</p>

      <div className="flex items-center justify-between pt-4 border-t border-border">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Calendar className="w-4 h-4" />
          <span>{article.journal || "PubMed"}</span>
        </div>
        <ExternalLink className="w-5 h-5 text-primary group-hover:translate-x-1 transition-transform" />
      </div>
    </a>
  );

  return (
    <>
      <TopBar
        title="Sağlık Makaleleri"
        subtitle="PubMed makalelerini arayın ve sağlık sorularınıza kısa yanıtlar alın."
      />

      {error && (
        <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg text-destructive">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 mb-8">
        <div className="xl:col-span-2 bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-foreground">Makale Arama</h3>
              <p className="text-sm text-muted-foreground">Örnek arama: glukoz, kolesterol, hemoglobin</p>
            </div>
            <Search className="w-5 h-5 text-primary" />
          </div>

          <div className="flex gap-3 mb-6">
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="PubMed üzerinde arayın..."
              className="flex-1 px-4 py-3 rounded-xl bg-surface border border-border text-foreground placeholder-muted-foreground outline-none focus:border-primary"
            />
            <button
              onClick={handleSearch}
              disabled={isSearching}
              className="px-5 py-3 rounded-xl bg-primary text-primary-foreground inline-flex items-center gap-2 disabled:opacity-50"
            >
              {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              Ara
            </button>
          </div>

          <h4 className="font-semibold text-foreground mb-3">Arama Sonuçları</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(searchResults.length > 0 ? searchResults : dailyArticles).map(renderArticleCard)}
          </div>
        </div>

        <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-foreground">Yapay Zeka Asistanı</h3>
              <p className="text-sm text-muted-foreground">Kısa sağlık soruları için sohbet</p>
            </div>
            <MessageCircle className="w-5 h-5 text-primary" />
          </div>

          <textarea
            value={chatMessage}
            onChange={(e) => setChatMessage(e.target.value)}
            placeholder="Örn: Kolesterol yüksekse ne yemeliyim?"
            className="w-full min-h-[140px] px-4 py-3 rounded-xl bg-surface border border-border text-foreground placeholder-muted-foreground outline-none focus:border-primary resize-none mb-3"
          />

          <button
            onClick={handleChat}
            disabled={isChatting}
            className="w-full px-5 py-3 rounded-xl bg-primary text-primary-foreground inline-flex items-center justify-center gap-2 disabled:opacity-50 mb-4"
          >
            {isChatting ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageCircle className="w-4 h-4" />}
            Yanıt Al
          </button>

          {chatAnswer && (
            <div className="p-4 rounded-xl bg-surface border border-border mb-4 overflow-y-auto max-h-[300px]">
              <div 
                className="text-sm text-foreground leading-relaxed"
                dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(chatAnswer.replace(/\n/g, '<br/>')) }}
              />
            </div>
          )}

          {chatSuggestions.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-semibold text-foreground">Öneriler</p>
              <div className="flex flex-col gap-2">
                {chatSuggestions.map((item) => (
                  <button
                    key={item}
                    onClick={() => {
                      setChatMessage(item);
                      handleChatDirect(item);
                    }}
                    className="w-full text-left text-sm text-muted-foreground px-4 py-3 rounded-xl bg-surface border border-border hover:bg-primary/5 hover:text-primary hover:border-primary/30 transition-all cursor-pointer group flex items-center justify-between"
                  >
                    <span>{item}</span>
                    <span className="opacity-0 group-hover:opacity-100 transition-opacity text-primary">→</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dailyArticles.length > 0 ? dailyArticles.map(renderArticleCard) : null}
      </div>
    </>
  );
}
