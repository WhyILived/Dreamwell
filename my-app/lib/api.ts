const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface User {
  id: number;
  email: string;
  company_name: string | null;
  website: string | null;
  keywords: string | null;
  country_code?: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  company_name?: string;
  website?: string;
  keywords?: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  access_token: string;
}

export interface ApiError {
  error: string;
}

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
    // Load token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('access_token', token);
      } else {
        localStorage.removeItem('access_token');
      }
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> | undefined),
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      if (response.status === 401 || response.status === 422) {
        this.setToken(null);
      }
      const error: ApiError = await response.json();
      throw new Error(error.error || 'An error occurred');
    }

    return response.json();
  }

  // Authentication methods
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
    
    this.setToken(response.access_token);
    return response;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
    
    this.setToken(response.access_token);
    return response;
  }

  async getProfile(): Promise<{ user: User }> {
    return this.request<{ user: User }>('/api/auth/profile');
  }

  async updateProfile(userData: Partial<User> & { country_code?: string | null }, userId?: number): Promise<{ user: User }> {
    // Get user ID from parameter or localStorage
    let user_id = userId;
    if (!user_id) {
      const user = JSON.parse(localStorage.getItem("user") || "{}");
      user_id = user.id;
    }
    
    if (!user_id) {
      throw new Error("User ID is required for profile update");
    }
    
    const dataWithId = {
      ...userData,
      id: user_id
    };
    
    return this.request<{ user: User }>('/api/auth/profile/simple', {
      method: 'PUT',
      body: JSON.stringify(dataWithId),
    });
  }

  logout() {
    this.setToken(null);
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Email methods
  async sendSponsorEmail(emailData: {
    influencer_name: string;
    influencer_email: string;
    product_name: string;
    custom_message?: string;
    suggested_pricing?: string;
    expected_profit?: string;
    influencer_data?: any;
  }): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('/api/auth/send-sponsor-email', {
      method: 'POST',
      body: JSON.stringify(emailData),
    });
  }

  async sendNotification(notificationData: {
    subject: string;
    message: string;
    influencer_count?: number;
  }): Promise<{ success: boolean; message: string }> {
    return this.request<{ success: boolean; message: string }>('/api/auth/send-notification', {
      method: 'POST',
      body: JSON.stringify(notificationData),
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
