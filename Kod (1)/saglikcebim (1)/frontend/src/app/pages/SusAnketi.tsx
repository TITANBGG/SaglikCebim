import { useState, useEffect } from "react";
import { Star, CheckCircle2, BarChart2, Loader2 } from "lucide-react";
import { TopBar } from "../components/TopBar";
import { apiClient } from "../../api/client";

const QUESTIONS = [
  "Bu sistemi sık sık kullanmak isterdim.",
  "Bu sistemi gereksiz yere karmaşık buldum.",
  "Bu sistemi kullanması kolay buldum.",
  "Bu sistemi kullanmak için uzman desteğine ihtiyaç duyduğumu düşünüyorum.",
  "Bu sistemin çeşitli fonksiyonlarının iyi entegre edildiğini gördüm.",
  "Bu sistemde çok fazla tutarsızlık olduğunu düşünüyorum.",
  "Çoğu insanın bu sistemi kullanmayı çabuk öğreneceğini düşünüyorum.",
  "Bu sistemi kullanmayı çok hantal buldum.",
  "Bu sistemi kullanırken kendimi güvende hissettim.",
  "Bu sistemi kullanmaya başlamadan önce çok şey öğrenmem gerektiğini hissettim.",
];

const LABELS = ["Kesinlikle Katılmıyorum", "Katılmıyorum", "Kararsızım", "Katılıyorum", "Kesinlikle Katılıyorum"];

export function SusAnketi() {
  const [scores, setScores] = useState<Record<string, number>>({});
  const [role, setRole] = useState("hasta");
  const [comment, setComment] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiClient.get("/api/v1/survey/results")
      .then(r => setStats(r.data))
      .catch(() => {});
  }, [submitted]);

  const setScore = (q: string, v: number) => setScores(prev => ({ ...prev, [q]: v }));

  const allAnswered = QUESTIONS.every((_, i) => scores[`q${i + 1}`] !== undefined);

  const handleSubmit = async () => {
    if (!allAnswered) return;
    setLoading(true);
    try {
      const r = await apiClient.post("/api/v1/survey/submit", { scores, role, comment });
      setResult(r.data);
      setSubmitted(true);
    } catch {
      alert("Gönderim başarısız. Lütfen tekrar deneyin.");
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = (s: number) => {
    if (s >= 85) return "text-emerald-500";
    if (s >= 72) return "text-blue-500";
    if (s >= 52) return "text-amber-500";
    return "text-red-500";
  };

  return (
    <>
      <TopBar
        title="Kullanıcı Memnuniyet Anketi"
        subtitle="SUS (System Usability Scale) — 10 soruluk standart kullanılabilirlik anketi"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Anket */}
        <div className="lg:col-span-2 bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          {submitted ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="w-8 h-8 text-emerald-500" />
              </div>
              <h3 className="text-2xl font-bold text-foreground mb-2">Teşekkürler!</h3>
              <p className="text-muted-foreground mb-6">Geri bildiriminiz kaydedildi.</p>
              {result && (
                <div className="inline-block bg-surface border border-border rounded-2xl p-6">
                  <p className="text-4xl font-bold mb-1 text-primary">{result.sus_score}</p>
                  <p className="text-sm text-muted-foreground">SUS Skorunuz</p>
                  <p className={`text-lg font-semibold mt-2 ${scoreColor(result.sus_score)}`}>{result.grade}</p>
                </div>
              )}
            </div>
          ) : (
            <>
              <h3 className="text-lg font-bold text-foreground mb-2">Lütfen her ifadeyi 1-5 arasında değerlendirin</h3>
              <p className="text-sm text-muted-foreground mb-6">1 = Kesinlikle Katılmıyorum, 5 = Kesinlikle Katılıyorum</p>

              <div className="space-y-6 mb-8">
                {QUESTIONS.map((q, i) => {
                  const key = `q${i + 1}`;
                  return (
                    <div key={key} className="p-4 bg-surface border border-border rounded-xl">
                      <p className="text-sm font-medium text-foreground mb-3">
                        <span className="text-primary font-bold mr-2">{i + 1}.</span>{q}
                      </p>
                      <div className="flex gap-2 flex-wrap">
                        {[1, 2, 3, 4, 5].map(v => (
                          <button
                            key={v}
                            onClick={() => setScore(key, v)}
                            className={`flex-1 min-w-[52px] py-2 rounded-lg text-sm font-medium transition-all border ${
                              scores[key] === v
                                ? "bg-primary text-white border-primary"
                                : "bg-background text-muted-foreground border-border hover:border-primary/50"
                            }`}
                          >
                            <span className="block text-center">{v}</span>
                            <span className="block text-[9px] text-center opacity-70 hidden sm:block">
                              {LABELS[v - 1].split(" ")[0]}
                            </span>
                          </button>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Rol seçimi */}
              <div className="mb-4">
                <label className="text-sm font-medium text-foreground mb-2 block">Rolünüz</label>
                <div className="flex gap-3 flex-wrap">
                  {["hasta", "hekim", "öğrenci", "araştırmacı"].map(r => (
                    <button
                      key={r}
                      onClick={() => setRole(r)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                        role === r
                          ? "bg-primary text-white border-primary"
                          : "bg-surface text-muted-foreground border-border hover:border-primary/50"
                      }`}
                    >
                      {r.charAt(0).toUpperCase() + r.slice(1)}
                    </button>
                  ))}
                </div>
              </div>

              {/* Yorum */}
              <div className="mb-6">
                <label className="text-sm font-medium text-foreground mb-2 block">Ek Yorumunuz (isteğe bağlı)</label>
                <textarea
                  value={comment}
                  onChange={e => setComment(e.target.value)}
                  maxLength={500}
                  rows={3}
                  placeholder="Sistem hakkındaki düşüncelerinizi paylaşın..."
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground resize-none focus:outline-none focus:border-primary/50"
                />
              </div>

              <button
                onClick={handleSubmit}
                disabled={!allAnswered || loading}
                className="w-full py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Star className="w-4 h-4" />}
                {allAnswered ? "Anketi Gönder" : `${Object.keys(scores).length}/10 soru yanıtlandı`}
              </button>
            </>
          )}
        </div>

        {/* İstatistikler */}
        <div className="space-y-4">
          <div className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
            <div className="flex items-center gap-2 mb-4">
              <BarChart2 className="w-5 h-5 text-primary" />
              <h3 className="font-bold text-foreground">Toplam Sonuçlar</h3>
            </div>
            {stats && stats.count > 0 ? (
              <>
                <p className={`text-4xl font-bold mb-1 ${scoreColor(stats.mean_sus)}`}>{stats.mean_sus}</p>
                <p className="text-sm text-muted-foreground mb-3">Ortalama SUS Skoru</p>
                <p className={`text-base font-semibold ${scoreColor(stats.mean_sus)}`}>{stats.grade}</p>
                <div className="mt-4 space-y-1 text-sm text-muted-foreground">
                  <p>{stats.count} kullanıcı değerlendirdi</p>
                  <p>Min: {stats.min_sus} | Maks: {stats.max_sus}</p>
                </div>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Henüz anket sonucu yok.</p>
            )}
          </div>

          <div className="bg-card border border-border rounded-[18px] p-6">
            <h4 className="font-bold text-foreground mb-3 text-sm">SUS Skor Kılavuzu</h4>
            <div className="space-y-2 text-xs">
              {[
                ["85-100", "A — Mükemmel", "text-emerald-500"],
                ["72-84", "B — İyi", "text-blue-500"],
                ["52-71", "C — Orta", "text-amber-500"],
                ["38-51", "D — Zayıf", "text-orange-500"],
                ["0-37",  "F — Kullanılamaz", "text-red-500"],
              ].map(([range, label, cls]) => (
                <div key={range} className="flex justify-between items-center">
                  <span className="text-muted-foreground">{range}</span>
                  <span className={`font-medium ${cls}`}>{label}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
