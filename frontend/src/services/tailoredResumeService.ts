import { authenticatedApiRequest } from "@/lib/api"
import type { MatchAnalysis } from "@/services/analysisService"

export interface ResumeContact {
  full_name: string | null
  email: string | null
  phone: string | null
  location: string | null
  links: string[]
}

export interface ResumeExperience {
  employer: string
  title: string
  location: string | null
  start_date: string | null
  end_date: string | null
  bullets: string[]
}

export interface ResumeEducation {
  institution: string
  degree: string | null
  field_of_study: string | null
  start_date: string | null
  end_date: string | null
  details: string[]
}

export interface ResumeProject {
  name: string
  description: string | null
  technologies: string[]
  bullets: string[]
}

export interface ResumeOptionalSection {
  heading: string
  items: string[]
}

export interface TailoredResumeContent {
  contact: ResumeContact
  summary: string | null
  experience: ResumeExperience[]
  education: ResumeEducation[]
  skills: string[]
  projects: ResumeProject[]
  optional_sections: ResumeOptionalSection[]
}

export interface TailoredResume {
  id: number
  user_id: number
  source_analysis_id: number
  source_resume_filename: string
  version_group_id: string
  version_number: number
  status: "draft" | "saved"
  content: TailoredResumeContent
  emphasized_items: string[]
  reordered_items: string[]
  match_snapshot: MatchAnalysis
  created_at: string
  updated_at: string
}

export interface TailoredResumeUpdate {
  content?: TailoredResumeContent
  status?: "draft" | "saved"
}

export async function generateTailoredResume(
  analysisId: number
): Promise<TailoredResume> {
  return authenticatedApiRequest<TailoredResume>(
    "/tailored-resumes",
    {
      method: "POST",
      body: JSON.stringify({
        analysis_id: analysisId,
      }),
    }
  )
}

export async function getTailoredResumes(): Promise<TailoredResume[]> {
  return authenticatedApiRequest<TailoredResume[]>(
    "/tailored-resumes"
  )
}

export async function getTailoredResume(
  id: number
): Promise<TailoredResume> {
  return authenticatedApiRequest<TailoredResume>(
    `/tailored-resumes/${id}`
  )
}

export async function updateTailoredResume(
  id: number,
  update: TailoredResumeUpdate
): Promise<TailoredResume> {
  return authenticatedApiRequest<TailoredResume>(
    `/tailored-resumes/${id}`,
    {
      method: "PATCH",
      body: JSON.stringify(update),
    }
  )
}

export async function deleteTailoredResume(
  id: number
): Promise<void> {
  await authenticatedApiRequest<{ message: string }>(
    `/tailored-resumes/${id}`,
    {
      method: "DELETE",
    }
  )
}