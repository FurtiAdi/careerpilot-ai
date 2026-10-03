import { apiRequest } from "@/lib/api"

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
}

export async function login(
  credentials: LoginRequest
): Promise<LoginResponse> {
  return apiRequest<LoginResponse>("/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  })
}

export interface RegisterRequest {
  fullName: string
  email: string
  password: string
}

export interface RegisterResponse {
  access_token: string
  token_type: "bearer"
}

export async function register(
  user: RegisterRequest
): Promise<RegisterResponse> {
  const formData = new FormData()

  formData.append("full_name", user.fullName)
  formData.append("email", user.email)
  formData.append("password", user.password)

  return apiRequest<RegisterResponse>(
    "/register",
    {
      method: "POST",
      body: formData,
    }
  )
}