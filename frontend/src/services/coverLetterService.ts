import { authenticatedApiRequest } from "@/lib/api"

export type CoverLetterTone =
  | "professional"
  | "warm"
  | "concise"

export type CoverLetterLength =
  | "short"
  | "standard"

export interface CoverLetterContent {
  opening: string
  evidence: string[]
  motivation: string
  closing: string
}

export interface CoverLetter {
  id: number
  user_id: number
  source_analysis_id: number
  source_resume_id: number
  source_tailored_resume_id: number | null
  version_group_id: string
  version_number: number
  status: "draft" | "saved"
  tone: CoverLetterTone
  length: CoverLetterLength
  content: CoverLetterContent
  created_at: string
  updated_at: string
}

export interface CoverLetterGenerationRequest {
  analysis_id: number
  source_resume_id: number
  source_tailored_resume_id?: number
  tone?: CoverLetterTone
  length?: CoverLetterLength
}

export interface CoverLetterUpdate {
  content?: CoverLetterContent
  status?: "draft" | "saved"
}

export async function generateCoverLetter(
  request: CoverLetterGenerationRequest
): Promise<CoverLetter> {
  return authenticatedApiRequest<CoverLetter>(
    "/cover-letters",
    {
      method: "POST",
      body: JSON.stringify(request),
    }
  )
}

export async function getCoverLetters(): Promise<
  CoverLetter[]
> {
  return authenticatedApiRequest<CoverLetter[]>(
    "/cover-letters"
  )
}

export async function getCoverLetter(
  id: number
): Promise<CoverLetter> {
  return authenticatedApiRequest<CoverLetter>(
    `/cover-letters/${id}`
  )
}

export async function downloadCoverLetterPdf(
  id: number
): Promise<Blob> {
  return authenticatedApiRequest<Blob>(
    `/cover-letters/${id}/export`,
    {
      method: "GET",
    },
    "blob"
  )
}

export async function regenerateCoverLetter(
  id: number
): Promise<CoverLetter> {
  return authenticatedApiRequest<CoverLetter>(
    `/cover-letters/${id}/regenerate`,
    {
      method: "POST",
    }
  )
}

export async function updateCoverLetter(
  id: number,
  update: CoverLetterUpdate
): Promise<CoverLetter> {
  return authenticatedApiRequest<CoverLetter>(
    `/cover-letters/${id}`,
    {
      method: "PATCH",
      body: JSON.stringify(update),
    }
  )
}

export async function deleteCoverLetter(
  id: number
): Promise<void> {
  await authenticatedApiRequest<{ message: string }>(
    `/cover-letters/${id}`,
    {
      method: "DELETE",
    }
  )
}
