import { User } from './user.model';

export interface UserRegisterRequest {
  name: string;
  email: string;
  password?: string;
}

export interface UserLoginRequest {
  email: string;
  password?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LogoutResponse {
  message: string;
}
