import { BookOpen, Calendar, Clock, ExternalLink } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { TopBar } from "../components/TopBar";

const articles = [
  {
    title: "Kan Tahlillerini Okuma Rehberi",
    excerpt: "Hemogram, biyokimya ve diğer kan tahlili değerlerinin ne anlama geldiğini öğrenin.",
    category: "Tahliller",
    date: "25 Nisan 2026",
    readTime: "8 dk",
    featured: true,
  },
  {
    title: "Tiroid Hormonları ve Yorumlanması",
    excerpt: "TSH, T3, T4 değerlerinin normal aralıkları ve sapmaların olası nedenleri.",
    category: "Hormonlar",
    date: "22 Nisan 2026",
    readTime: "6 dk",
    featured: true,
  },
  {
    title: "Lipid Profili Nedir?",
    excerpt: "Kolesterol, HDL, LDL ve trigliserid değerlerinin kalp sağlığı üzerindeki etkileri.",
    category: "Kardiyoloji",
    date: "20 Nisan 2026",
    readTime: "7 dk",
    featured: false,
  },
  {
    title: "Göğüs Röntgeni Bulguları",
    excerpt: "Toraks grafilerinde sık karşılaşılan bulguların klinik anlamları.",
    category: "Radyoloji",
    date: "18 Nisan 2026",
    readTime: "10 dk",
    featured: false,
  },
  {
    title: "Vitamin D Eksikliği ve Sonuçları",
    excerpt: "D vitamini düşüklüğünün belirtileri, nedenleri ve tedavi yaklaşımları.",
    category: "Vitaminler",
    date: "15 Nisan 2026",
    readTime: "5 dk",
    featured: false,
  },
  {
    title: "Şeker Hastalığı Takibi",
    excerpt: "HbA1c, açlık kan şekeri ve tokluk şekeri testlerinin değerlendirilmesi.",
    category: "Endokrinoloji",
    date: "12 Nisan 2026",
    readTime: "9 dk",
    featured: false,
  },
  {
    title: "Böbrek Fonksiyon Testleri",
    excerpt: "Kreatinin, üre ve GFR değerlerinin böbrek sağlığı açısından önemi.",
    category: "Nefroloji",
    date: "10 Nisan 2026",
    readTime: "6 dk",
    featured: false,
  },
  {
    title: "Karaciğer Enzimlerini Anlamak",
    excerpt: "ALT, AST, ALP ve GGT yüksekliğinin olası sebepleri ve klinik yaklaşım.",
    category: "Hepatoloji",
    date: "8 Nisan 2026",
    readTime: "7 dk",
    featured: false,
  },
];

const categories = [
  "Tümü",
  "Tahliller",
  "Hormonlar",
  "Kardiyoloji",
  "Radyoloji",
  "Vitaminler",
  "Endokrinoloji",
  "Nefroloji",
  "Hepatoloji",
];

export function Makaleler() {
  return (
    <>
      <TopBar
        title="Sağlık Makaleleri"
        subtitle="Sağlık ve tahlil sonuçları hakkında bilgilendirici içerikler."
      />

      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((category, index) => (
          <button
            key={category}
            className={`px-4 py-2 rounded-xl transition-all ${
              index === 0
                ? "bg-primary text-primary-foreground shadow-[0_0_20px_rgba(45,212,255,0.15)]"
                : "bg-card border border-border text-muted-foreground hover:bg-card-hover hover:text-foreground"
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {articles
          .filter((article) => article.featured)
          .map((article, index) => (
            <div
              key={index}
              className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)] hover:bg-card-hover hover:border-border-strong transition-all cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-4">
                <Badge className="bg-primary/10 text-primary border-primary/20">
                  {article.category}
                </Badge>
                <div className="flex items-center gap-2 text-muted-foreground text-sm">
                  <Clock className="w-4 h-4" />
                  <span>{article.readTime}</span>
                </div>
              </div>

              <h3 className="text-xl font-bold text-foreground mb-3 group-hover:text-primary transition-colors">
                {article.title}
              </h3>
              <p className="text-muted-foreground mb-4 leading-relaxed">
                {article.excerpt}
              </p>

              <div className="flex items-center justify-between pt-4 border-t border-border">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Calendar className="w-4 h-4" />
                  <span>{article.date}</span>
                </div>
                <ExternalLink className="w-5 h-5 text-primary group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles
          .filter((article) => !article.featured)
          .map((article, index) => (
            <div
              key={index}
              className="bg-card border border-border rounded-[18px] p-6 shadow-[0_10px_30px_rgba(2,8,23,0.24)] hover:bg-card-hover hover:border-border-strong transition-all cursor-pointer group"
            >
              <div className="flex items-center gap-2 mb-3">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-primary" />
                </div>
                <Badge className="bg-surface text-foreground border-border text-xs">
                  {article.category}
                </Badge>
              </div>

              <h4 className="font-bold text-foreground mb-2 group-hover:text-primary transition-colors">
                {article.title}
              </h4>
              <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
                {article.excerpt}
              </p>

              <div className="flex items-center justify-between text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  <span>{article.date}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  <span>{article.readTime}</span>
                </div>
              </div>
            </div>
          ))}
      </div>
    </>
  );
}
