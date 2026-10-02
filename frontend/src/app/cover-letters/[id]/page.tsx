"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"

import {
  downloadCoverLetterPdf,
  getCoverLetter,
  regenerateCoverLetter,
  updateCoverLetter,
  type CoverLetter,
} from "@/services/coverLetterService"


export default function CoverLetterPreviewPage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const coverLetterId = Number(params.id)
  const validCoverLetterId =
    Number.isInteger(coverLetterId) &&
    coverLetterId > 0

  const [coverLetter, setCoverLetter] =
    useState<CoverLetter | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [regenerating, setRegenerating] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [copying, setCopying] = useState(false)
  const [copySuccess, setCopySuccess] = useState<string | null>(null)
  const [actionError, setActionError] =
    useState<string | null>(null)
  const [draftOpening, setDraftOpening] = useState("")
  const [draftEvidence, setDraftEvidence] = useState("")
  const [draftMotivation, setDraftMotivation] =
    useState("")
  const [draftClosing, setDraftClosing] = useState("")

  useEffect(() => {
    if (!validCoverLetterId) {
      return
    }

    let cancelled = false

    const loadCoverLetter = async () => {
      try {
        const data = await getCoverLetter(coverLetterId)

        if (!cancelled) {
          setCoverLetter(data)
        }
      } catch (error) {
        if (!cancelled) {
          setError(
            error instanceof Error
              ? error.message
              : "Failed to load cover letter."
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadCoverLetter()

    return () => {
      cancelled = true
    }
  }, [coverLetterId, validCoverLetterId])

  const beginEditing = () => {
    if (!coverLetter) {
      return
    }

    setDraftOpening(coverLetter.content.opening)
    setDraftEvidence(coverLetter.content.evidence.join("\n"))
    setDraftMotivation(coverLetter.content.motivation)
    setDraftClosing(coverLetter.content.closing)
    setActionError(null)
    setEditing(true)
  }

  const cancelEditing = () => {
    setDraftOpening("")
    setDraftEvidence("")
    setDraftMotivation("")
    setDraftClosing("")
    setActionError(null)
    setEditing(false)
  }

  const saveCoverLetterEdits = async () => {
    if (!coverLetter) {
      return
    }

    try {
      setSaving(true)
      setActionError(null)

      const updatedLetter = await updateCoverLetter(
        coverLetter.id,
        {
          content: {
            opening: draftOpening.trim(),
            evidence: draftEvidence
              .split("\n")
              .map((item) => item.trim())
              .filter(Boolean),
            motivation: draftMotivation.trim(),
            closing: draftClosing.trim(),
          },
          status: "saved",
        }
      )

      setCoverLetter(updatedLetter)
      setEditing(false)
      router.replace(`/cover-letters/${updatedLetter.id}`)
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : "Failed to save cover letter."
      )
    } finally {
      setSaving(false)
    }
  }

  const regenerateCoverLetterVersion = async () => {
    if (!coverLetter) {
        return
    }

    try {
        setRegenerating(true)
        setActionError(null)
        setCopySuccess(null)

        const regeneratedLetter = await regenerateCoverLetter(
        coverLetter.id
        )

        setCoverLetter(regeneratedLetter)
        setEditing(false)
        router.replace(`/cover-letters/${regeneratedLetter.id}`)
    } catch (error) {
        setActionError(
        error instanceof Error
            ? error.message
            : "Failed to regenerate cover letter."
        )
    } finally {
        setRegenerating(false)
    }
}

  const downloadPdf = async () => {
    if (!coverLetter) {
      return
    }

    try {
      setDownloading(true)
      setActionError(null)

      const pdfBlob = await downloadCoverLetterPdf(coverLetter.id)
      const downloadUrl = URL.createObjectURL(pdfBlob)
      const link = document.createElement("a")

      link.href = downloadUrl
      link.download = `cover-letter-${coverLetter.id}.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.setTimeout(() => URL.revokeObjectURL(downloadUrl), 0)
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : "Failed to download cover letter."
      )
    } finally {
      setDownloading(false)
    }
  }

  const copyCoverLetter = async () => {
    if (!coverLetter) {
      return
    }

    const copyText = [
      coverLetter.content.opening,
      ...coverLetter.content.evidence,
      coverLetter.content.motivation,
      coverLetter.content.closing,
    ]
      .filter(Boolean)
      .join("\n\n")

    try {
      setCopying(true)
      setCopySuccess(null)
      setActionError(null)

      await navigator.clipboard.writeText(copyText)
      setCopySuccess("Cover letter copied to clipboard.")
    } catch (error) {
      setActionError(
        error instanceof Error
          ? error.message
          : "Failed to copy cover letter."
      )
    } finally {
      setCopying(false)
    }
  }

  if (!validCoverLetterId) {
    return (
      <main className="min-h-screen bg-black px-6 pt-28 text-white">
        <p className="text-red-300">
          Invalid cover letter ID.
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

  if (error || !coverLetter) {
    return (
      <main className="min-h-screen bg-black px-6 pt-28 text-white">
        <div className="mx-auto max-w-3xl rounded-2xl border border-red-500/30 bg-red-500/10 p-6">
          <p className="text-red-200">
            {error ?? "Cover letter not found."}
          </p>

          <Link
            href="/history"
            className="mt-4 inline-block text-purple-300 hover:text-purple-200"
          >
            Return to analysis history
          </Link>
        </div>
      </main>
    )
  }

  const { content } = coverLetter

  return (
    <main className="min-h-screen bg-black px-6 py-28 text-white">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-purple-300">
              Version {coverLetter.version_number} ·{" "}
              {coverLetter.status}
            </p>

            <h1 className="mt-2 text-4xl font-bold">
              Cover Letter Preview
            </h1>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
                onClick={regenerateCoverLetterVersion}
                disabled={
                    editing ||
                    saving ||
                    regenerating ||
                    downloading ||
                    copying
                }
                className="rounded-xl border border-purple-500 px-4 py-2 font-medium text-purple-200 hover:bg-purple-500/10 disabled:cursor-not-allowed disabled:opacity-60"
                >
                {regenerating ? "Regenerating..." : "Regenerate"}
            </button>

            {editing ? (
              <>
                <button
                  onClick={cancelEditing}
                  disabled={saving || regenerating}
                  className="rounded-xl border border-white/10 px-4 py-2 text-gray-300 disabled:opacity-50"
                >
                  Cancel
                </button>

                <button
                  onClick={saveCoverLetterEdits}
                  disabled={saving || regenerating}
                  className="rounded-xl bg-purple-600 px-4 py-2 font-semibold text-white hover:bg-purple-500 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save version"}
                </button>
              </>
            ) : (
              <button
                onClick={beginEditing}
                disabled={regenerating}
                className="rounded-xl bg-purple-600 px-4 py-2 font-semibold text-white hover:bg-purple-500"
              >
                Edit cover letter
              </button>
            )}

            <button
              onClick={copyCoverLetter}
              disabled={editing || saving || downloading || copying || regenerating}
              className="rounded-xl border border-purple-500 px-4 py-2 font-medium text-purple-200 hover:bg-purple-500/10 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {copying ? "Copying..." : "Copy"}
            </button>

            <button
              onClick={downloadPdf}
              disabled={editing || saving || downloading || regenerating}
              className="rounded-xl border border-purple-500 px-4 py-2 font-medium text-purple-200 hover:bg-purple-500/10 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {downloading ? "Preparing PDF..." : "Download PDF"}
            </button>

            <Link
              href="/history"
              className="rounded-xl border border-white/10 px-4 py-2 text-gray-300 hover:border-purple-500/40"
            >
              Back to history
            </Link>
          </div>
        </div>

        {actionError && (
          <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
            {actionError}
          </div>
        )}

        {copySuccess && (
          <div className="mb-6 rounded-2xl border border-green-500/30 bg-green-500/10 px-5 py-4 text-green-200">
            {copySuccess}
          </div>
        )}

        <article className="rounded-3xl bg-white p-8 text-gray-900 shadow-2xl md:p-12">
          {editing ? (
            <div className="space-y-6">
              <label className="block font-semibold">
                Opening
                <textarea
                  value={draftOpening}
                  onChange={(event) =>
                    setDraftOpening(event.target.value)
                  }
                  className="mt-2 min-h-28 w-full rounded-xl border border-purple-300 p-4 font-normal text-gray-900"
                />
              </label>

              <label className="block font-semibold">
                Evidence
                <span className="mt-1 block text-sm font-normal text-gray-500">
                  Enter one verified experience statement per line.
                </span>
                <textarea
                  value={draftEvidence}
                  onChange={(event) =>
                    setDraftEvidence(event.target.value)
                  }
                  className="mt-2 min-h-36 w-full rounded-xl border border-purple-300 p-4 font-normal text-gray-900"
                />
              </label>

              <label className="block font-semibold">
                Motivation
                <textarea
                  value={draftMotivation}
                  onChange={(event) =>
                    setDraftMotivation(event.target.value)
                  }
                  className="mt-2 min-h-28 w-full rounded-xl border border-purple-300 p-4 font-normal text-gray-900"
                />
              </label>

              <label className="block font-semibold">
                Closing
                <textarea
                  value={draftClosing}
                  onChange={(event) =>
                    setDraftClosing(event.target.value)
                  }
                  className="mt-2 min-h-28 w-full rounded-xl border border-purple-300 p-4 font-normal text-gray-900"
                />
              </label>
            </div>
          ) : (
            <>
              <p className="whitespace-pre-wrap leading-8">
                {content.opening}
              </p>

              {content.evidence.length > 0 && (
                <ul className="my-6 list-disc space-y-2 pl-6 leading-8">
                  {content.evidence.map((item, index) => (
                    <li key={`${item}-${index}`}>{item}</li>
                  ))}
                </ul>
              )}

              <p className="whitespace-pre-wrap leading-8">
                {content.motivation}
              </p>

              <p className="mt-6 whitespace-pre-wrap leading-8">
                {content.closing}
              </p>
            </>
          )}
        </article>
      </div>
    </main>
  )
}
