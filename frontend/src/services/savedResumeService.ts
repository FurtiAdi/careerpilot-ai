import { authenticatedApiRequest } from "@/lib/api"

export interface SavedResume {
  id: number
  original_filename: string
  created_at: string
}

export async function getSavedResumes(): Promise<SavedResume[]> {
  return authenticatedApiRequest<SavedResume[]>(
    "/saved-resumes"
  )
}

export async function uploadSavedResume(
  file: File
): Promise<SavedResume> {
  const formData = new FormData()
  formData.append("file", file)

  return authenticatedApiRequest<SavedResume>(
    "/saved-resumes",
    {
      method: "POST",
      body: formData,
    }
  )
}
