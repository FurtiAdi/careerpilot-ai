"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import {
  type ChangeEvent,
  type FormEvent,
  useEffect,
  useState,
} from "react"
import {
  AlertCircle,
  CheckCircle2,
  FileText,
  FileUp,
  LoaderCircle,
} from "lucide-react"

import {
  type SavedResume,
  uploadSavedResume,
} from "@/services/savedResumeService"

const MAX_RESUME_SIZE_BYTES = 5 * 1024 * 1024

export default function CvOnboardingPage() {
  const router = useRouter()

  const [selectedFile, setSelectedFile] = useState<File | null>(
    null
  )
  const [uploadedResume, setUploadedResume] =
    useState<SavedResume | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      router.replace("/login?next=/onboarding/cv")
    }
  }, [router])

  const selectFile = (
    event: ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0] ?? null

    setError(null)
    setSelectedFile(null)

    if (!file) {
      return
    }

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please choose a PDF resume.")
      return
    }

    if (file.size > MAX_RESUME_SIZE_BYTES) {
      setError("Your resume must not exceed 5 MiB.")
      return
    }

    setSelectedFile(file)
  }

  const uploadCv = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault()

    if (!selectedFile) {
      setError("Choose a PDF resume before continuing.")
      return
    }

    try {
      setLoading(true)
      setError(null)

      const savedResume = await uploadSavedResume(
        selectedFile
      )

      setUploadedResume(savedResume)
      setSelectedFile(null)
    } catch (uploadError) {
      setError(
        uploadError instanceof Error
          ? uploadError.message
          : "We could not upload your resume. Please try again."
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-6 pb-12 pt-28 text-slate-900">
      <div className="pointer-events-none absolute left-0 top-24 h-72 w-72 rounded-full bg-purple-200/50 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 rounded-full bg-pink-100/70 blur-3xl" />

      <section className="relative mx-auto flex min-h-[calc(100vh-10rem)] max-w-2xl items-center">
        <div className="w-full rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-purple-950/10 sm:p-10">
          <div className="mb-8">
            <p className="mb-3 text-sm font-semibold text-purple-600">
              Step 2 of 4
            </p>

            <div className="mb-8 h-2 overflow-hidden rounded-full bg-slate-100">
              <div className="h-full w-1/2 rounded-full bg-gradient-to-r from-purple-600 to-pink-500" />
            </div>

            <h1 className="text-3xl font-bold tracking-tight text-slate-950">
              Upload your CV
            </h1>

            <p className="mt-3 max-w-xl leading-6 text-slate-600">
              Upload your CV so CareerPilot can use your verified
              background in the next onboarding steps.
            </p>
          </div>

          {uploadedResume ? (
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6">
              <div className="flex items-start gap-4">
                <CheckCircle2 className="mt-0.5 h-6 w-6 shrink-0 text-emerald-600" />

                <div>
                  <h2 className="font-semibold text-emerald-950">
                    Your CV has been uploaded
                  </h2>

                  <p className="mt-1 text-sm text-emerald-800">
                    {uploadedResume.original_filename} is saved securely
                    and ready for profile review in the next onboarding
                    milestone.
                  </p>
                </div>
              </div>

              <Link
                href="/"
                className="mt-6 inline-flex h-11 items-center justify-center rounded-xl border border-emerald-300 bg-white px-4 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-100"
              >
                Back to home
              </Link>
            </div>
          ) : (
            <form
              onSubmit={uploadCv}
              className="space-y-5"
            >
              <label
                htmlFor="resume-file"
                className="flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-purple-200 bg-purple-50/40 p-8 text-center transition hover:border-purple-400 hover:bg-purple-50"
              >
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-600 to-pink-500 text-white shadow-lg shadow-purple-500/25">
                  <FileUp className="h-7 w-7" />
                </div>

                <span className="mt-5 text-lg font-semibold text-slate-900">
                  Drag and drop your CV here
                </span>

                <span className="mt-2 text-sm text-slate-600">
                  or click to browse
                </span>

                <span className="mt-4 text-sm text-slate-500">
                  PDF only · Maximum file size 5 MiB
                </span>

                <input
                  id="resume-file"
                  type="file"
                  accept=".pdf,application/pdf"
                  onChange={selectFile}
                  disabled={loading}
                  className="sr-only"
                />
              </label>

              {selectedFile && (
                <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                  <FileText className="h-5 w-5 shrink-0 text-purple-600" />

                  <div className="min-w-0">
                    <p className="truncate text-sm font-semibold text-slate-900">
                      {selectedFile.name}
                    </p>

                    <p className="text-xs text-slate-500">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                </div>
              )}

              {error && (
                <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                  <AlertCircle className="mt-0.5 h-5 w-5 shrink-0" />

                  <p>{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 font-semibold text-white shadow-lg shadow-purple-500/25 transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? (
                  <>
                    <LoaderCircle className="h-5 w-5 animate-spin" />
                    Uploading CV...
                  </>
                ) : (
                  "Upload CV"
                )}
              </button>
            </form>
          )}
        </div>
      </section>
    </main>
  )
}