import { authenticatedApiRequest } from "@/lib/api"

export interface Analysis {
  id: number
  job_description: string
  candidate_skills: string
  match_score: number
  ai_summary: string
  created_at: string
}

export interface AnalyzeJobRequest {
  job_description: string
  candidate_skills: string[]
}

export interface ResumeUploadResponse {
  filename: string
  extracted_text: string
  detected_skills: string[]
}

export async function getAnalyses(): Promise<Analysis[]> {
  return authenticatedApiRequest<Analysis[]>("/analyses")
}

export async function deleteAnalysisById(
  id: number
): Promise<void> {
  await authenticatedApiRequest<void>(
    `/analyses/${id}`,
    {
      method: "DELETE",
    }
  )
}

export async function analyzeJobRequest(
  data: AnalyzeJobRequest
) {
  return authenticatedApiRequest("/analyze-job", {
    method: "POST",
    body: JSON.stringify(data),
  })
}

export async function uploadResumeFile(
  file: File
): Promise<ResumeUploadResponse> {
  const formData = new FormData()
  formData.append("file", file)

  return authenticatedApiRequest<ResumeUploadResponse>(
    "/upload-resume",
    {
      method: "POST",
      body: formData,
    }
  )
}