import { useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import { Mail, Lock, User, AlertCircle } from "lucide-react";

export function LoginPage() {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    // Client-side validation
    if (!email || !password) {
      setError("Email ve şifre gereklidir");
      setIsLoading(false);
      return;
    }

    if (!isLogin && !fullName) {
      setError("Ad Soyad gereklidir");
      setIsLoading(false);
      return;
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Lütfen geçerli bir email girin");
      setIsLoading(false);
      return;
    }

    // Password validation for register
    if (!isLogin && password.length < 8) {
      setError("Şifre en az 8 karakter olmalıdır");
      setIsLoading(false);
      return;
    }

    try {
      if (isLogin) {
        await login(email, password);
      } else {
        await register(email, password, fullName);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "Bir hata oluştu";
      
      // Translate common errors
      const errorMap: { [key: string]: string } = {
        "Email already registered": "Bu email zaten kayıtlı",
        "Invalid credentials": "Email veya şifre hatalı",
        "Invalid user ID": "Kullanıcı kimliği hatalı",
        "User not found": "Kullanıcı bulunamadı"
      };
      
      setError(errorMap[errorMessage] || errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="dark min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-card border border-border rounded-[18px] p-8 shadow-[0_10px_30px_rgba(2,8,23,0.24)]">
          {/* Logo/Header */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <div className="text-2xl">🏥</div>
            </div>
            <h1 className="text-2xl font-bold text-foreground mb-2">SağlıkCebim</h1>
            <p className="text-sm text-muted-foreground">Sağlık Analiz Platformu</p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg flex gap-3">
              <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Ad Soyad
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Ad Soyad"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    disabled={isLoading}
                    className="w-full pl-10 pr-4 py-2.5 bg-surface border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary disabled:opacity-50"
                  />
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
                <input
                  type="email"
                  placeholder="email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-surface border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary disabled:opacity-50"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-foreground mb-2">
                Şifre
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-3 w-5 h-5 text-muted-foreground" />
                <input
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  required
                  className="w-full pl-10 pr-4 py-2.5 bg-surface border border-border rounded-lg text-foreground placeholder-muted-foreground focus:outline-none focus:border-primary disabled:opacity-50"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full mt-6 py-2.5 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Bekleniyor..." : isLogin ? "Giriş Yap" : "Kayıt Ol"}
            </button>
          </form>

          {/* Toggle */}
          <div className="mt-6 text-center">
            <p className="text-sm text-muted-foreground">
              {isLogin ? "Hesabın yok mu?" : "Zaten hesabın var mı?"}{" "}
              <button
                type="button"
                onClick={() => {
                  setIsLogin(!isLogin);
                  setError("");
                }}
                className="text-primary font-medium hover:underline"
              >
                {isLogin ? "Kayıt Ol" : "Giriş Yap"}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
