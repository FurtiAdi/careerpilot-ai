import { authenticatedApiRequest } from "@/lib/api"

export interface CareerProfileContact {
  full_name: string | null
  headline: string | null
  email: string | null
  phone: string | null
  location: string | null
  links: string[]
}

export interface CareerProfileExperience {
  title: string
  employer: string | null
  location: string | null
  start_date: string | null
  end_date: string | null
  bullets: string[]
}

export interface CareerProfileEducation {
  institution: string
  degree: string | null
  field_of_study: string | null
  start_date: string | null
  end_date: string | null
  details: string[]
}

export interface CareerProfileCertificate {
  name: string
  issuer: string | null
  date: string | null
  details: string[]
}

export interface CareerProfileContent {
  contact: CareerProfileContact
  experience: CareerProfileExperience[]
  education: CareerProfileEducation[]
  skills: string[]
  certificates: CareerProfileCertificate[]
}

export interface CareerProfile {
  id: number
  user_id: number
  source_resume_id: number
  status: "draft" | "reviewed"
  content: CareerProfileContent
  created_at: string
  updated_at: string
}

export async function extractCareerProfile(
  sourceResumeId: number
): Promise<CareerProfile> {
  return authenticatedApiRequest<CareerProfile>(
    "/career-profiles/extract",
    {
      method: "POST",
      body: JSON.stringify({
        source_resume_id: sourceResumeId,
      }),
    }
  )
}