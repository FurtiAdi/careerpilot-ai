"use client"

import { useEffect, useState, type FormEvent } from "react"

import { useRouter } from "next/navigation"

import {
  createApplication,
  type Application,
  type ApplicationStatus,
} from "@/services/applicationService"
import { getAnalyses, type Analysis } from "@/services/analysisService"
import {
  getTailoredResumes,
  type TailoredResume,
} from "@/services/tailoredResumeService"
import {
  getCoverLetters,
  type CoverLetter,
} from "@/services/coverLetterService"

const applicationStatuses: ApplicationStatus[] = [
  "saved",
  "applied",
  "screening",
  "interview",
  "offer",
  "rejected",
  "withdrawn",
]

function formatStatus(status: ApplicationStatus): string {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

interface ApplicationCreationFormProps {
  onCreated?: (application: Application) => void
}

export default function ApplicationCreationForm({
  onCreated,
}: ApplicationCreationFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [company, setCompany] = useState("")
  const [role, setRole] = useState("")
  const [status, setStatus] = useState<ApplicationStatus>("saved")
  const [jobUrl, setJobUrl] = useState("")
  const [jobDescription, setJobDescription] = useState("")
  const [appliedAt, setAppliedAt] = useState("")
  const [nextActionDate, setNextActionDate] = useState("")
  const [notes, setNotes] = useState("")
  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [tailoredResumes, setTailoredResumes] = useState<TailoredResume[]>([])
  const [coverLetters, setCoverLetters] = useState<CoverLetter[]>([])
  const [selectedAnalysisId, setSelectedAnalysisId] = useState<number | null>(null)
  const [selectedTailoredResumeId, setSelectedTailoredResumeId] =
    useState<number | null>(null)
  const [selectedCoverLetterId, setSelectedCoverLetterId] =
    useState<number | null>(null)

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
      return
    }

    let cancelled = false

    const loadRelatedDocuments = async () => {
      try {
        setError(null)

        const [analysisData, tailoredResumeData, coverLetterData] =
          await Promise.all([
            getAnalyses(),
            getTailoredResumes(),
            getCoverLetters(),
          ])

        if (!cancelled) {
          setAnalyses(analysisData)
          setTailoredResumes(tailoredResumeData)
          setCoverLetters(coverLetterData)
        }
      } catch (error) {
        if (!cancelled) {
          setError(
            error instanceof Error
              ? error.message
              : "Failed to load related documents."
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadRelatedDocuments()

    return () => {
      cancelled = true
    }
  }, [router])

  const createTrackedApplication = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault()

    if (!company.trim() || !role.trim()) {
      setError("Company and role are required.")
      return
    }

    try {
      setCreating(true)
      setError(null)

      const application = await createApplication({
        company: company.trim(),
        role: role.trim(),
        status,
        job_url: jobUrl.trim() || undefined,
        job_description: jobDescription.trim() || undefined,
        applied_at: appliedAt || undefined,
        next_action_date: nextActionDate || undefined,
        notes: notes.trim() || undefined,
        analysis_id: selectedAnalysisId ?? undefined,
        tailored_resume_id: selectedTailoredResumeId ?? undefined,
        cover_letter_id: selectedCoverLetterId ?? undefined,
      })

      setCompany("")
      setRole("")
      setStatus("saved")
      setJobUrl("")
      setJobDescription("")
      setAppliedAt("")
      setNextActionDate("")
      setNotes("")
      setSelectedAnalysisId(null)
      setSelectedTailoredResumeId(null)
      setSelectedCoverLetterId(null)

      if (onCreated) {
        onCreated(application)
        return
      }

      router.push("/applications")
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to create application."
      )
    } finally {
      setCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="py-10 text-center">
        <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-purple-500/20 border-t-purple-400" />
      </div>
    )
  }

  return (
    <>
      {error && (
        <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
          {error}
        </div>
      )}

      <form
        onSubmit={createTrackedApplication}
        className="grid gap-4 md:grid-cols-2"
      >
        <label className="text-sm text-gray-300">
          Company
          <input
            value={company}
            onChange={(event) => setCompany(event.target.value)}
            required
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
            placeholder="Example Corp"
          />
        </label>

        <label className="text-sm text-gray-300">
          Role
          <input
            value={role}
            onChange={(event) => setRole(event.target.value)}
            required
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
            placeholder="Backend Engineer"
          />
        </label>

        <label className="text-sm text-gray-300">
          Status
          <select
            value={status}
            onChange={(event) =>
              setStatus(event.target.value as ApplicationStatus)
            }
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
          >
            {applicationStatuses.map((item) => (
              <option key={item} value={item}>
                {formatStatus(item)}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-gray-300">
          Job URL
          <input
            type="url"
            value={jobUrl}
            onChange={(event) => setJobUrl(event.target.value)}
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
            placeholder="https://example.com/jobs/123"
          />
        </label>

        <label className="text-sm text-gray-300">
          Applied date
          <input
            type="date"
            value={appliedAt}
            onChange={(event) => setAppliedAt(event.target.value)}
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
          />
        </label>

        <label className="text-sm text-gray-300">
          Next action date
          <input
            type="date"
            value={nextActionDate}
            onChange={(event) => setNextActionDate(event.target.value)}
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
          />
        </label>

        <label className="text-sm text-gray-300 md:col-span-2">
          Job description snapshot
          <textarea
            value={jobDescription}
            onChange={(event) => setJobDescription(event.target.value)}
            disabled={creating}
            className="mt-2 min-h-32 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
            placeholder="Optional: paste the job description you applied to."
          />
        </label>

        <label className="text-sm text-gray-300 md:col-span-2">
          Notes
          <textarea
            value={notes}
            onChange={(event) => setNotes(event.target.value)}
            disabled={creating}
            className="mt-2 min-h-28 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
            placeholder="Optional follow-up or application notes."
          />
        </label>

        <label className="text-sm text-gray-300">
          Related analysis
          <select
            value={selectedAnalysisId ?? ""}
            onChange={(event) =>
              setSelectedAnalysisId(
                event.target.value ? Number(event.target.value) : null
              )
            }
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
          >
            <option value="">No linked analysis</option>
            {analyses.map((analysis) => (
              <option key={analysis.id} value={analysis.id}>
                Analysis #{analysis.id} · {analysis.match_score}% match
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-gray-300">
          Tailored resume version
          <select
            value={selectedTailoredResumeId ?? ""}
            onChange={(event) =>
              setSelectedTailoredResumeId(
                event.target.value ? Number(event.target.value) : null
              )
            }
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
          >
            <option value="">No linked tailored resume</option>
            {tailoredResumes.map((resume) => (
              <option key={resume.id} value={resume.id}>
                Resume version {resume.version_number} · Analysis #
                {resume.source_analysis_id}
              </option>
            ))}
          </select>
        </label>

        <label className="text-sm text-gray-300 md:col-span-2">
          Cover letter version
          <select
            value={selectedCoverLetterId ?? ""}
            onChange={(event) =>
              setSelectedCoverLetterId(
                event.target.value ? Number(event.target.value) : null
              )
            }
            disabled={creating}
            className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
          >
            <option value="">No linked cover letter</option>
            {coverLetters.map((coverLetter) => (
              <option key={coverLetter.id} value={coverLetter.id}>
                Cover letter version {coverLetter.version_number} · Analysis #
                {coverLetter.source_analysis_id}
              </option>
            ))}
          </select>
        </label>

        <div className="md:col-span-2">
          <button
            type="submit"
            disabled={creating}
            className="rounded-xl bg-purple-600 px-5 py-3 font-semibold text-white hover:bg-purple-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {creating ? "Saving..." : "Save application"}
          </button>
        </div>
      </form>
    </>
  )
}
