import { authenticatedApiRequest } from "@/lib/api"

export interface User {
  id: number
  full_name: string
  email: string
  profile_picture_filename?: string | null
}

export async function getCurrentUser(): Promise<User> {
  return authenticatedApiRequest<User>("/me")
}