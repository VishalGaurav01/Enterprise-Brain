export interface Permission {
  id: string;
  name: string;
  code: string;
}

export interface Role {
  id: string;
  name: string;
  description?: string;
  permissions: Permission[];
}

export interface User {
  id: string;
  username: string;
  email: string;
  status: string;
  is_superuser: boolean;
  created_at: string;
  roles: Role[];
}

export interface TokenResponse {
  session_token: string;
  token_type: string;
  user: User;
  expires_at: string;
}
