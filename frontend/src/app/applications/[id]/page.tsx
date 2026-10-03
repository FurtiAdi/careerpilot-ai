"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"

import {
  deleteApplication,
  getApplication,
  getApplicationEvents,
  updateApplication,
  type Application,
  type ApplicationEvent,
  type ApplicationStatus,
} from "@/services/applicationService"

function formatStatus(status: ApplicationStatus): string {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

function formatDate(value: string | null): string {
  if (!value) {
    return "Not set"
  }

  return new Date(`${value}T00:00:00`).toLocaleDateString()
}

export default function ApplicationDetailPage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const applicationId = Number(params.id)
  const validApplicationId =
    Number.isInteger(applicationId) && applicationId > 0

  const [application, setApplication] =
    useState<Application | null>(null)
  const [events, setEvents] = useState<ApplicationEvent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [actionError, setActionError] =
    useState<string | null>(null)
  const [draftStatus, setDraftStatus] =
    useState<ApplicationStatus>("saved")
  const [draftNextActionDate, setDraftNextActionDate] =
    useState("")
  const [draftNotes, setDraftNotes] = useState("")

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
      return
    }

    if (!validApplicationId) {
      return
    }

    let cancelled = false

    const loadApplication = async () => {
      try {
        setError(null)

        const [applicationData, eventData] = await Promise.all([
          getApplication(applicationId),
          getApplicationEvents(applicationId),
        ])

        if (!cancelled) {
          setApplication(applicationData)
          setEvents(eventData)
        }
      } catch (error) {
        if (!cancelled) {
          setError(
            error instanceof Error
              ? error.message
              : "Failed to load application."
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadApplication()

    return () => {
      cancelled = true
    }
  }, [applicationId, router, validApplicationId])

  const beginEditing = () => {
    if (!application) {
      return
    }

    setDraftStatus(application.status)
    setDraftNextActionDate(
      application.next_action_date ?? ""
    )
    setDraftNotes(application.notes ?? "")
    setActionError(null)
    setEditing(true)
  }

  const cancelEditing = () => {
    setActionError(null)
    setEditing(false)
  }

  const saveApplicationEdits = async () => {
    if (!application) {
      return
    }

    try {
      setSaving(true)
      setActionError(null)

      const updatedApplication = await updateApplication(
        application.id,
        {
            status: draftStatus,
            next_action_date: draftNextActionDate || null,
            notes: draftNotes.trim() || null,
        }
        )

        const updatedEvents = await getApplicationEvents(
        application.id
        )

      setApplication(updatedApplication)
      setEvents(updatedEvents)
      setEditing(false)
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : "Failed to update application."
      )
    } finally {
      setSaving(false)
    }
  }

  const deleteCurrentApplication = async () => {
    if (!application) {
      return
    }

    const confirmed = window.confirm(
      "Delete this application and its status history?"
    )

    if (!confirmed) {
      return
    }

    try {
      setDeleting(true)
      setActionError(null)

      await deleteApplication(application.id)
      router.replace("/applications")
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : "Failed to delete application."
      )
    } finally {
      setDeleting(false)
    }
  }

  if (!validApplicationId) {
    return (
      <main className="min-h-screen bg-black px-6 pt-28 text-white">
        <p className="text-red-300">
          Invalid application ID.
        </p>
      </main>
    )
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-black pt-40 text-center">
        <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-purple-500/20 border-t-purple-400" />
      </main>
    )
  }

  if (error || !application) {
    return (
      <main className="min-h-screen bg-black px-6 pt-28 text-white">
        <div className="mx-auto max-w-3xl rounded-2xl border border-red-500/30 bg-red-500/10 p-6">
          <p className="text-red-200">
            {error ?? "Application not found."}
          </p>

          <Link
            href="/applications"
            className="mt-4 inline-block text-purple-300 hover:text-purple-200"
          >
            Return to applications
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-black px-6 py-28 text-white">
      <div className="mx-auto max-w-5xl">
        <div className="mb-10 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm text-purple-300">
              {formatStatus(application.status)}
            </p>

            <h1 className="mt-2 text-4xl font-bold">
              {application.role}
            </h1>

            <p className="mt-2 text-xl text-gray-300">
              {application.company}
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            {editing ? (
              <>
                <button
                  onClick={cancelEditing}
                  disabled={saving || deleting}
                  className="rounded-xl border border-white/10 px-4 py-2 font-semibold text-gray-300 disabled:opacity-50"
                >
                  Cancel
                </button>

                <button
                  onClick={saveApplicationEdits}
                  disabled={saving || deleting}
                  className="rounded-xl bg-purple-600 px-4 py-2 font-semibold text-white hover:bg-purple-500 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save changes"}
                </button>
              </>
            ) : (
              <button
                onClick={beginEditing}
                disabled={deleting}
                className="rounded-xl bg-purple-600 px-4 py-2 font-semibold text-white hover:bg-purple-500"
              >
                Edit application
              </button>
            )}

            <button
              onClick={deleteCurrentApplication}
              disabled={saving || deleting}
              className="rounded-xl border border-red-500/40 px-4 py-2 font-semibold text-red-300 hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {deleting ? "Deleting..." : "Delete"}
            </button>

            <Link
              href="/applications"
              className="rounded-xl border border-purple-500/40 px-4 py-2 font-semibold text-purple-200 hover:bg-purple-500/10"
            >
              Back to applications
            </Link>
          </div>
        </div>

        {actionError && (
          <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
            {actionError}
          </div>
        )}

        <section className="grid gap-4 md:grid-cols-3">
          <article className="rounded-2xl border border-purple-500/20 bg-purple-500/10 p-5">
            <p className="text-sm text-purple-200">Status</p>

            <p className="mt-2 text-2xl font-semibold">
              {formatStatus(application.status)}
            </p>
          </article>

          <article className="rounded-2xl border border-yellow-500/20 bg-yellow-500/10 p-5">
            <p className="text-sm text-yellow-200">
              Applied date
            </p>

            <p className="mt-2 text-2xl font-semibold">
              {formatDate(application.applied_at)}
            </p>
          </article>

          <article className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-5">
            <p className="text-sm text-blue-200">
              Next action
            </p>

            <p className="mt-2 text-2xl font-semibold">
              {formatDate(application.next_action_date)}
            </p>
          </article>
        </section>

        {editing && (
          <section className="mt-10 rounded-3xl border border-purple-500/20 bg-purple-500/10 p-6">
            <h2 className="text-2xl font-semibold text-purple-200">
              Update application
            </h2>

            <div className="mt-5 grid gap-4 md:grid-cols-2">
              <label className="text-sm text-gray-300">
                Status
                <select
                  value={draftStatus}
                  onChange={(event) =>
                    setDraftStatus(
                      event.target.value as ApplicationStatus
                    )
                  }
                  disabled={saving}
                  className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
                >
                  <option value="saved">Saved</option>
                  <option value="applied">Applied</option>
                  <option value="screening">Screening</option>
                  <option value="interview">Interview</option>
                  <option value="offer">Offer</option>
                  <option value="rejected">Rejected</option>
                  <option value="withdrawn">Withdrawn</option>
                </select>
              </label>

              <label className="text-sm text-gray-300">
                Next action date
                <input
                  type="date"
                  value={draftNextActionDate}
                  onChange={(event) =>
                    setDraftNextActionDate(event.target.value)
                  }
                  disabled={saving}
                  className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
                />
              </label>

              <label className="text-sm text-gray-300 md:col-span-2">
                Notes
                <textarea
                  value={draftNotes}
                  onChange={(event) =>
                    setDraftNotes(event.target.value)
                  }
                  disabled={saving}
                  className="mt-2 min-h-28 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
                />
              </label>
            </div>
          </section>
        )}

        <section className="mt-10 grid gap-6 lg:grid-cols-2">
          <article className="rounded-3xl border border-white/10 bg-white/5 p-6">
            <h2 className="text-2xl font-semibold text-purple-200">
              Linked CareerPilot records
            </h2>

            <div className="mt-5 space-y-4 text-gray-300">
              <div>
                <p className="text-sm text-gray-500">Analysis</p>
                {application.analysis_id ? (
                  <Link
                    href="/history"
                    className="text-purple-300 hover:text-purple-200"
                  >
                    Analysis #{application.analysis_id}
                  </Link>
                ) : (
                  <p>Not linked</p>
                )}
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  Tailored resume
                </p>
                {application.tailored_resume_id ? (
                  <Link
                    href={`/tailored-resumes/${application.tailored_resume_id}`}
                    className="text-purple-300 hover:text-purple-200"
                  >
                    Open linked tailored resume
                  </Link>
                ) : (
                  <p>Not linked</p>
                )}
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  Cover letter
                </p>
                {application.cover_letter_id ? (
                  <Link
                    href={`/cover-letters/${application.cover_letter_id}`}
                    className="text-purple-300 hover:text-purple-200"
                  >
                    Open linked cover letter
                  </Link>
                ) : (
                  <p>Not linked</p>
                )}
              </div>
            </div>
          </article>

          <article className="rounded-3xl border border-white/10 bg-white/5 p-6">
            <h2 className="text-2xl font-semibold text-pink-200">
              Application details
            </h2>

            <div className="mt-5 space-y-4 text-gray-300">
              <div>
                <p className="text-sm text-gray-500">Job URL</p>
                {application.job_url ? (
                  <a
                    href={application.job_url}
                    target="_blank"
                    rel="noreferrer"
                    className="break-all text-purple-300 hover:text-purple-200"
                  >
                    {application.job_url}
                  </a>
                ) : (
                  <p>Not provided</p>
                )}
              </div>

              <div>
                <p className="text-sm text-gray-500">
                  Job description snapshot
                </p>
                <p className="mt-1 whitespace-pre-wrap">
                  {application.job_description ?? "Not provided"}
                </p>
              </div>

              <div>
                <p className="text-sm text-gray-500">Notes</p>
                <p className="mt-1 whitespace-pre-wrap">
                  {application.notes ?? "No notes yet."}
                </p>
              </div>
            </div>
          </article>
        </section>

        <section className="mt-10 rounded-3xl border border-pink-500/20 bg-pink-500/10 p-6">
          <h2 className="text-2xl font-semibold text-pink-200">
            Status history
          </h2>

          {events.length === 0 ? (
            <p className="mt-4 text-gray-400">
              No status events are available yet.
            </p>
          ) : (
            <ol className="mt-5 space-y-4 border-l border-pink-500/30 pl-5">
              {events.map((event) => (
                <li key={event.id}>
                  <p className="font-semibold">
                    {event.previous_status
                      ? `${formatStatus(
                          event.previous_status
                        )} → `
                      : ""}
                    {formatStatus(event.new_status)}
                  </p>

                  {event.note && (
                    <p className="mt-1 text-gray-300">
                      {event.note}
                    </p>
                  )}

                  <p className="mt-1 text-sm text-gray-500">
                    {new Date(
                      event.created_at
                    ).toLocaleString()}
                  </p>
                </li>
              ))}
            </ol>
          )}
        </section>
      </div>
    </main>
  )
}
