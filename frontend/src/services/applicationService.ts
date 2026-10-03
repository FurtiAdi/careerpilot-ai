import { authenticatedApiRequest } from "@/lib/api"

export type ApplicationStatus =
  | "saved"
  | "applied"
  | "screening"
  | "interview"
  | "offer"
  | "rejected"
  | "withdrawn"

export interface Application {
  id: number
  user_id: number
  company: string
  role: string
  status: ApplicationStatus
  job_url: string | null
  job_description: string | null
  applied_at: string | null
  next_action_date: string | null
  notes: string | null
  analysis_id: number | null
  tailored_resume_id: number | null
  cover_letter_id: number | null
  created_at: string
  updated_at: string
}

export interface ApplicationEvent {
  id: number
  application_id: number
  user_id: number
  event_type: "status_changed"
  previous_status: ApplicationStatus | null
  new_status: ApplicationStatus
  note: string | null
  created_at: string
}

export interface ApplicationCreateRequest {
  company: string
  role: string
  status?: ApplicationStatus
  job_url?: string
  job_description?: string
  applied_at?: string
  next_action_date?: string
  notes?: string
  analysis_id?: number
  tailored_resume_id?: number
  cover_letter_id?: number
}

export interface ApplicationUpdateRequest {
  company?: string
  role?: string
  status?: ApplicationStatus
  job_url?: string | null
  job_description?: string | null
  applied_at?: string | null
  next_action_date?: string | null
  notes?: string | null
  analysis_id?: number | null
  tailored_resume_id?: number | null
  cover_letter_id?: number | null
}

export async function createApplication(
  request: ApplicationCreateRequest
): Promise<Application> {
  return authenticatedApiRequest<Application>(
    "/applications",
    {
      method: "POST",
      body: JSON.stringify(request),
    }
  )
}

export async function getApplications(): Promise<
  Application[]
> {
  return authenticatedApiRequest<Application[]>(
    "/applications"
  )
}

export async function getApplication(
  id: number
): Promise<Application> {
  return authenticatedApiRequest<Application>(
    `/applications/${id}`
  )
}

export async function updateApplication(
  id: number,
  request: ApplicationUpdateRequest
): Promise<Application> {
  return authenticatedApiRequest<Application>(
    `/applications/${id}`,
    {
      method: "PATCH",
      body: JSON.stringify(request),
    }
  )
}

export async function deleteApplication(
  id: number
): Promise<void> {
  await authenticatedApiRequest<{ message: string }>(
    `/applications/${id}`,
    {
      method: "DELETE",
    }
  )
}

export async function getApplicationEvents(
  id: number
): Promise<ApplicationEvent[]> {
  return authenticatedApiRequest<ApplicationEvent[]>(
    `/applications/${id}/events`
  )
}