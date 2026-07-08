import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      // Global Content-Type TANIMLANMIYOR — FormData isteklerinde Axios'un
      // otomatik olarak multipart/form-data+boundary eklemesine izin verilir.
      // JSON istekler için Content-Type her metotta ayrıca eklenir.
    });

    // Load token from localStorage
    this.token = localStorage.getItem('auth_token');
    this.updateAuthHeader();

    // Add response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Sadece gerçek token süresi dolumu (401) durumunda oturumu kapat.
        // Upload/parse gibi işlemlerdeki 422 hatalarının oturumu kapatmaması için
        // kontrol yapılıyor: istek URL'si /auth/ ile başlamıyorsa ve status 401 ise.
        const isAuthEndpoint = error.config?.url?.includes('/auth/');
        if (error.response?.status === 401 && !isAuthEndpoint) {
          this.clearAuth();
          window.location.href = '/';
        }
        return Promise.reject(error);
      }
    );
  }

  private updateAuthHeader() {
    if (this.token) {
      this.client.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;
    } else {
      delete this.client.defaults.headers.common['Authorization'];
    }
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('auth_token', token);
    this.updateAuthHeader();
  }

  clearAuth() {
    this.token = null;
    localStorage.removeItem('auth_token');
    delete this.client.defaults.headers.common['Authorization'];
  }

  get(url: string, config?: AxiosRequestConfig) {
    return this.client.get(url, config);
  }

  post(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return this.client.post(url, data, config);
  }

  put(url: string, data?: unknown, config?: AxiosRequestConfig) {
    return this.client.put(url, data, config);
  }

  delete(url: string, config?: AxiosRequestConfig) {
    return this.client.delete(url, config);
  }

  // Auth endpoints
  async register(email: string, password: string, fullName: string) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  }

  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', {
      email,
      password,
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  // Reports endpoints
  async uploadReport(formData: FormData) {
    // Content-Type header'ını manuel set etme — Axios, FormData ile birlikte
    // boundary'yi otomatik ekler. Manuel set edilirse boundary eksik kalır → 422 hatası.
    const response = await this.client.post('/reports/upload', formData);
    return response.data;
  }

  async listReports() {
    const response = await this.client.get('/reports/');
    return response.data;
  }

  async getReportResults(reportId: string) {
    const response = await this.client.get(`/reports/${reportId}/results`);
    return response.data;
  }

  async getReportRecommendations(reportId: string) {
    const response = await this.client.get(`/reports/${reportId}/recommendations`);
    return response.data;
  }

  async getReportPubmed(reportId: string) {
    const response = await this.client.post(`/reports/${reportId}/pubmed`);
    return response.data;
  }

  async downloadReportPdf(reportId: string) {
    const response = await this.client.get(`/reports/${reportId}/download-pdf`, {
      responseType: 'blob',
    });
    return response.data;
  }

  async parseReport(reportId: string) {
    const response = await this.client.post(`/reports/${reportId}/parse`);
    return response.data;
  }

  async deleteReport(reportId: string) {
    const response = await this.client.delete(`/reports/${reportId}`);
    return response.data;
  }

  async getDashboardMonitoring() {
    const response = await this.client.get('/reports/monitoring');
    return response.data;
  }

  async getTrends(testName: string) {
    const response = await this.client.get(`/reports/trends/${testName}`);
    return response.data;
  }

  async getAvailableTests() {
    const response = await this.client.get('/reports/available-tests');
    return response.data;
  }

  // Radiology endpoints
  async uploadRadiology(formData: FormData) {
    // Content-Type header'ını manuel set etme — Axios, FormData ile birlikte
    // boundary'yi otomatik ekler. Manuel set edilirse boundary eksik kalır → 422 hatası.
    const response = await this.client.post('/radiology/upload', formData);
    return response.data;
  }

  async listRadiology() {
    const response = await this.client.get('/radiology/');
    return response.data;
  }

  async getRadiologyDetails(imageId: number) {
    const response = await this.client.get(`/radiology/${imageId}`);
    return response.data;
  }

  // Articles endpoints
  async getDailyArticles() {
    const response = await this.client.get('/articles/daily');
    return response.data;
  }

  async searchArticles(query: string, limit: number = 10) {
    const response = await this.client.post('/articles/search', {
      query,
      limit,
    });
    return response.data;
  }

  async chatAboutArticles(message: string, articleId?: string) {
    const response = await this.client.post('/articles/chat', {
      message,
      article_id: articleId,
    });
    return response.data;
  }

  async chatAnamnesis(message: string, context?: Record<string, unknown>) {
    const response = await this.client.post('/api/v1/anamnesis/chat', {
      message,
      context,
    });
    return response.data;
  }

  // Chatbot endpoint - kişiye özel sağlık asistanı
  async chatbotChat(
    message: string,
    conversationHistory: Array<{ role: string; content: string }> = [],
    reportId?: string,
    sessionId?: number
  ) {
    const response = await this.client.post('/api/v1/chatbot/chat', {
      message,
      conversation_history: conversationHistory,
      report_id: reportId || null,
      session_id: sessionId,
    });
    return response.data;
  }

  async getChatSessions() {
    const response = await this.client.get('/api/v1/chatbot/sessions');
    return response.data;
  }

  async getChatMessages(sessionId: number) {
    const response = await this.client.get(`/api/v1/chatbot/sessions/${sessionId}`);
    return response.data;
  }

  // Health check
  async health() {
    const response = await this.client.get('/health');
    return response.data;
  }

  async testClinicalKey(query: string) {
    const response = await this.client.post('/api/v1/evidence/test', { query });
    return response.data;
  }

  async getPatientSummary() {
    const response = await this.client.get('/patient/summary/basic');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
