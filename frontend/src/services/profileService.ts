import { authenticatedApiRequest } from "@/lib/api"
import { Analysis } from "./analysisService"
import { User } from "./userService"

export interface ProfileStats {
  total_analyses: number
  average_match_score: number
  resume_uploaded: boolean
}

export interface UploadProfilePictureResponse {
  profile_picture_filename: string
}

export async function getProfile(): Promise<User> {
  return authenticatedApiRequest<User>("/me")
}

export async function getProfileStats(): Promise<ProfileStats> {
  return authenticatedApiRequest<ProfileStats>("/profile-stats")
}

export async function getRecentAnalyses(): Promise<Analysis[]> {
  return authenticatedApiRequest<Analysis[]>("/analyses")
}

export async function uploadProfilePicture(
  file: File
): Promise<UploadProfilePictureResponse> {
  const formData = new FormData()

  formData.append("file", file)

  return authenticatedApiRequest<UploadProfilePictureResponse>(
    "/upload-profile-picture",
    {
      method: "POST",
      body: formData,
    }
  )
}