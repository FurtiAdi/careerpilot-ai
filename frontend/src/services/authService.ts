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
  resumeFile?: File | null
  profileImage?: File | null
}

export interface RegisterResponse {
  message?: string
}

export async function register(
  user: RegisterRequest
): Promise<RegisterResponse> {
  const formData = new FormData()

  formData.append("full_name", user.fullName)
  formData.append("email", user.email)
  formData.append("password", user.password)

  if (user.resumeFile) {
    formData.append("resume", user.resumeFile)
  }

  if (user.profileImage) {
    formData.append(
      "profile_picture",
      user.profileImage
    )
  }

  return apiRequest<RegisterResponse>(
    "/register",
    {
      method: "POST",
      body: formData,
    }
  )
}