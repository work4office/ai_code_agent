export interface UserProfile {
  id: string;
  name: string;
  email: string;
}

export interface AuthContextType {
  user: UserProfile | null;
  accessToken: string | null;
  login: (credentials: Record<string, string>) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

export interface LoginResponse {
  access_token: string;
  user: UserProfile;
}

export interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
}

export interface CreateUserResponse {
  id: number;
  name: string;
  email: string;
  is_active: boolean;
}

export interface LoginRequest {
  name: string;
  email: string;
  [key: string]: string;
}
