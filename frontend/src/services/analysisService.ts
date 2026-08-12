import { authenticatedApiRequest } from "@/lib/api"

export interface Analysis {
  id: number
  job_description: string
  candidate_skills: string
  match_score: number
  ai_summary: string
  created_at: string
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