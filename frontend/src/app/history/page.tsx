"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

import {
  Analysis,
  getAnalyses,
  deleteAnalysisById,
} from "@/services/analysisService"

import {
  deleteTailoredResume,
  generateTailoredResume,
  getTailoredResumes,
  type TailoredResume,
} from "@/services/tailoredResumeService"
import {
  getSavedResumes,
  uploadSavedResume,
  type SavedResume,
} from "@/services/savedResumeService"
import {
  generateCoverLetter,
  getCoverLetters,
  type CoverLetter,
  type CoverLetterLength,
  type CoverLetterTone,
} from "@/services/coverLetterService"

export default function HistoryPage() {

  const [analyses, setAnalyses] = useState<Analysis[]>([])
  const [tailoredResumes, setTailoredResumes] =
    useState<TailoredResume[]>([])
  const [coverLetters, setCoverLetters] =
    useState<CoverLetter[]>([])
  const [savedResumes, setSavedResumes] =
    useState<SavedResume[]>([])
  const [selectedSavedResumeId, setSelectedSavedResumeId] =
    useState<number | null>(null)
  const [selectedResumeFile, setSelectedResumeFile] =
    useState<File | null>(null)
  const [uploadingResume, setUploadingResume] =
    useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] =
    useState<string | null>(null)
  const [generatingAnalysisId, setGeneratingAnalysisId] =
    useState<number | null>(null)
  const [
    generatingCoverLetterAnalysisId,
    setGeneratingCoverLetterAnalysisId,
  ] = useState<number | null>(null)
  const [coverLetterTone, setCoverLetterTone] =
    useState<CoverLetterTone>("professional")
  const [coverLetterLength, setCoverLetterLength] =
    useState<CoverLetterLength>("standard")
  const [deletingTailoredResumeId, setDeletingTailoredResumeId] =
    useState<number | null>(null)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("token")

    if (!token) {
      router.push("/login")
      return
    }

    let cancelled = false

    const loadHistory = async () => {
      try {
        setError(null)

        const [
          analysisData,
          tailoredResumeData,
          savedResumeData,
          coverLetterData,
        ] = await Promise.all([
          getAnalyses(),
          getTailoredResumes(),
          getSavedResumes(),
          getCoverLetters(),
        ])

        if (!cancelled) {
          setAnalyses(analysisData)
          setTailoredResumes(tailoredResumeData)
          setSavedResumes(savedResumeData)
          setCoverLetters(coverLetterData)
          setSelectedSavedResumeId((current) =>
            current ?? savedResumeData[0]?.id ?? null
          )
        }
      } catch (error) {
        if (!cancelled) {
          setError(
            error instanceof Error
              ? error.message
              : "Failed to load history."
          )
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    void loadHistory()

    return () => {
      cancelled = true
    }
  }, [router])

  const deleteAnalysis = async (
    id: number
  ) => {
    try {
      setError(null)

      await deleteAnalysisById(id)

      setAnalyses((prev) =>
        prev.filter(
          (analysis) =>
            analysis.id !== id
        )
      )
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to delete analysis."
      )
    }
  }

  const deleteTailoredResumeCard = async (
    id: number
  ) => {
    try {
      setError(null)
      setDeletingTailoredResumeId(id)

      await deleteTailoredResume(id)

      setTailoredResumes((previous) =>
        previous.filter(
          (resume) => resume.id !== id
        )
      )
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to delete tailored resume."
      )
    } finally {
      setDeletingTailoredResumeId(null)
    }
  }

  const generateResume = async (
    analysisId: number
  ) => {
    if (selectedSavedResumeId === null) {
      setError(
        "Upload and select a saved resume before generating."
      )
      return
    }

    try {
      setError(null)
      setGeneratingAnalysisId(analysisId)

      const tailoredResume =
        await generateTailoredResume(
          analysisId,
          selectedSavedResumeId
        )

      router.push(
        `/tailored-resumes/${tailoredResume.id}`
      )
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to generate tailored resume."
      )
    } finally {
      setGeneratingAnalysisId(null)
    }
  }

  const generateLetter = async (
    analysisId: number
  ) => {
    if (selectedSavedResumeId === null) {
      setError(
        "Upload and select a saved resume before generating."
      )
      return
    }

    try {
      setError(null)
      setGeneratingCoverLetterAnalysisId(analysisId)

      const coverLetter = await generateCoverLetter({
        analysis_id: analysisId,
        source_resume_id: selectedSavedResumeId,
        tone: coverLetterTone,
        length: coverLetterLength,
      })

      router.push(`/cover-letters/${coverLetter.id}`)
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to generate cover letter."
      )
    } finally {
      setGeneratingCoverLetterAnalysisId(null)
    }
  }

  const uploadSourceResume = async () => {
    if (selectedResumeFile === null) {
      setError("Choose a PDF resume to upload.")
      return
    }

    try {
      setError(null)
      setUploadingResume(true)

      const savedResume = await uploadSavedResume(
        selectedResumeFile
      )

      setSavedResumes((previous) => [
        savedResume,
        ...previous,
      ])
      setSelectedSavedResumeId(savedResume.id)
      setSelectedResumeFile(null)
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Failed to upload the source resume."
      )
    } finally {
      setUploadingResume(false)
    }
  }

  const getScoreColor = (
    score: number
  ) => {

    if (score >= 80) {
      return "text-green-400"
    }

    if (score >= 50) {
      return "text-purple-400"
    }

    return "text-red-400"
  }

  return (

    <main className="min-h-screen pt-28 bg-black text-white px-10 py-16">

      <div className="max-w-5xl mx-auto">

        <h1 className="text-4xl font-bold mb-10 bg-gradient-to-r from-purple-400 to-pink-500 text-transparent bg-clip-text">
          Analysis History
        </h1>

        {error && (
          <div
            className="
              mb-6
              rounded-2xl
              border border-red-500/30
              bg-red-500/10
              px-5 py-4
              text-red-200
            "
          >
            {error}
          </div>
        )}

        <section className="mb-10 rounded-2xl border border-purple-500/20 bg-purple-500/10 p-5">
          <h2 className="text-xl font-semibold text-purple-200">
            Source Resume
          </h2>

          <p className="mt-1 text-sm text-gray-400">
            Select the verified resume that will ground new tailored versions.
          </p>

          <div className="mt-4 flex flex-wrap items-center gap-3">
            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={(event) =>
                setSelectedResumeFile(
                  event.target.files?.[0] ?? null
                )
              }
              disabled={uploadingResume}
              className="block text-sm text-gray-300 file:mr-4 file:rounded-lg file:border-0 file:bg-purple-500/20 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-purple-200 hover:file:bg-purple-500/30"
            />

            <button
              type="button"
              onClick={uploadSourceResume}
              disabled={
                selectedResumeFile === null ||
                uploadingResume
              }
              className="rounded-xl border border-purple-500/40 px-4 py-2 text-sm font-semibold text-purple-200 hover:bg-purple-500/10 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {uploadingResume
                ? "Uploading..."
                : "Upload resume"}
            </button>
          </div>

          {selectedResumeFile !== null && (
            <p className="mt-2 text-sm text-gray-400">
              Ready to upload: {selectedResumeFile.name}
            </p>
          )}

          {savedResumes.length === 0 ? (
            <p className="mt-4 text-sm text-yellow-200">
              No saved resumes are available yet.
            </p>
          ) : (
            <select
              value={selectedSavedResumeId ?? ""}
              onChange={(event) =>
                setSelectedSavedResumeId(
                  Number(event.target.value)
                )
              }
              className="mt-4 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
            >
              {savedResumes.map((resume) => (
                <option
                  key={resume.id}
                  value={resume.id}
                >
                  {resume.original_filename}
                </option>
              ))}
            </select>
          )}
          <div className="mt-4 grid gap-3 md:grid-cols-2">
            <label className="text-sm text-gray-300">
              Tone
              <select
                value={coverLetterTone}
                onChange={(event) =>
                  setCoverLetterTone(
                    event.target.value as CoverLetterTone
                  )
                }
                className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
              >
                <option value="professional">
                  Professional
                </option>
                <option value="warm">Warm</option>
                <option value="concise">Concise</option>
              </select>
            </label>

            <label className="text-sm text-gray-300">
              Length
              <select
                value={coverLetterLength}
                onChange={(event) =>
                  setCoverLetterLength(
                    event.target.value as CoverLetterLength
                  )
                }
                className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-4 py-3 text-white"
              >
                <option value="standard">Standard</option>
                <option value="short">Short</option>
              </select>
            </label>
          </div>
        </section>

        {!loading && tailoredResumes.length > 0 && (
          <section className="mb-10">
            <div className="mb-5">
              <h2 className="text-2xl font-semibold text-purple-200">
                Tailored Resumes
              </h2>

              <p className="mt-1 text-gray-400">
                Open a saved resume version or continue editing it.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {tailoredResumes.map((resume) => (
                <article
                  key={resume.id}
                  className="rounded-2xl border border-purple-500/20 bg-purple-500/10 p-5"
                >
                  <p className="text-sm text-purple-300">
                    Analysis #{resume.source_analysis_id}
                  </p>

                  <h3 className="mt-2 text-lg font-semibold">
                    {resume.content.contact.full_name ??
                      "Tailored Resume"}
                  </h3>

                  <p className="mt-1 text-sm text-gray-400">
                    Version {resume.version_number} · {resume.status}
                  </p>

                  <p className="mt-1 text-sm text-gray-500">
                    Updated{" "}
                    {new Date(
                      resume.updated_at
                    ).toLocaleDateString()}
                  </p>

                  <button
                    onClick={() =>
                      router.push(
                        `/tailored-resumes/${resume.id}`
                      )
                    }
                    className="mt-4 rounded-xl border border-purple-500/40 px-4 py-2 text-sm font-semibold text-purple-200 hover:bg-purple-500/10"
                  >
                    Open resume
                  </button>
                  <button
                    onClick={() => {
                      const confirmed = window.confirm(
                        "Delete this tailored resume version?"
                      )

                      if (confirmed) {
                        void deleteTailoredResumeCard(resume.id)
                      }
                    }}
                    disabled={deletingTailoredResumeId !== null}
                    className="ml-3 rounded-xl border border-red-500/30 px-4 py-2 text-sm font-semibold text-red-300 hover:bg-red-500/10 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    {deletingTailoredResumeId === resume.id
                      ? "Deleting..."
                      : "Delete"}
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}

        {!loading && coverLetters.length > 0 && (
          <section className="mb-10">
            <div className="mb-5">
              <h2 className="text-2xl font-semibold text-pink-200">
                Cover Letters
              </h2>

              <p className="mt-1 text-gray-400">
                Open a generated cover letter or continue editing it.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {coverLetters.map((coverLetter) => (
                <article
                  key={coverLetter.id}
                  className="rounded-2xl border border-pink-500/20 bg-pink-500/10 p-5"
                >
                  <p className="text-sm text-pink-300">
                    Analysis #{coverLetter.source_analysis_id}
                  </p>

                  <h3 className="mt-2 text-lg font-semibold">
                    Cover Letter
                  </h3>

                  <p className="mt-1 text-sm text-gray-400">
                    Version {coverLetter.version_number} ·{" "}
                    {coverLetter.status}
                  </p>

                  <p className="mt-1 text-sm text-gray-500">
                    {coverLetter.tone} · {coverLetter.length}
                  </p>

                  <p className="mt-1 text-sm text-gray-500">
                    Updated{" "}
                    {new Date(
                      coverLetter.updated_at
                    ).toLocaleDateString()}
                  </p>

                  <button
                    onClick={() =>
                      router.push(
                        `/cover-letters/${coverLetter.id}`
                      )
                    }
                    className="mt-4 rounded-xl border border-pink-500/40 px-4 py-2 text-sm font-semibold text-pink-200 hover:bg-pink-500/10"
                  >
                    Open cover letter
                  </button>
                </article>
              ))}
            </div>
          </section>
        )}

        <div className="grid gap-6">

          {loading && (

            <div className="text-center py-20">

              <div className="inline-block w-10 h-10 border-4 border-purple-500/20 border-t-purple-400 rounded-full animate-spin" />

            </div>

          )}

          {!loading && analyses.length === 0 && (

            <div
              className="
                text-center
                py-20
                border border-white/10
                rounded-3xl
                bg-white/5
              "
            >

              <h2 className="text-2xl font-semibold mb-4">
                No Analyses Yet
              </h2>

              <p className="text-gray-400">
                Your saved job analyses will appear here.
              </p>

            </div>

          )}

          {analyses.map((analysis) => (

            <div
              key={analysis.id}
              className="
                bg-gradient-to-br from-white/5 to-purple-500/5
                border border-white/10
                rounded-3xl
                p-8
                transition-all
                duration-300
                hover:scale-[1.01]
                hover:border-purple-500/30
              "
            >

              <div className="flex items-start justify-between mb-8">

                <div>

                  <h2 className="text-2xl font-semibold">
                    Analysis #{analysis.id}
                  </h2>

                  <p className="text-sm text-gray-500 mt-2">
                    {new Date(
                      analysis.created_at
                    ).toLocaleDateString()}
                  </p>

                </div>

                <div className="text-right">

                  <p className="text-sm text-gray-500 mb-2">
                    Match Score
                  </p>

                  <div
                    className={`
                      text-4xl font-bold
                      ${getScoreColor(analysis.match_score)}
                    `}
                  >
                    {analysis.match_score}%
                  </div>
                  <button
                    onClick={() => generateResume(analysis.id)}
                    disabled={
                      generatingAnalysisId !== null ||
                      selectedSavedResumeId === null
                    }
                    className="
                      mt-4 ml-auto block px-4 py-2
                      rounded-xl
                      bg-purple-500/20
                      border border-purple-500/30
                      text-purple-200
                      hover:bg-purple-500/30
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                      transition-all duration-300
                    "
                  >
                    {generatingAnalysisId === analysis.id
                      ? "Generating..."
                      : "Generate Tailored Resume"}
                  </button>

                  <button
                    onClick={() => generateLetter(analysis.id)}
                    disabled={
                      generatingCoverLetterAnalysisId !== null ||
                      selectedSavedResumeId === null
                    }
                    className="
                      mt-3 ml-auto block px-4 py-2
                      rounded-xl
                      bg-pink-500/20
                      border border-pink-500/30
                      text-pink-200
                      hover:bg-pink-500/30
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                      transition-all duration-300
                    "
                  >
                    {generatingCoverLetterAnalysisId === analysis.id
                      ? "Generating..."
                      : "Generate Cover Letter"}
                  </button>

                  <button
                    onClick={() => {

                      const confirmed = confirm(
                        "Delete this analysis?"
                      )

                      if (confirmed) {
                        deleteAnalysis(analysis.id)
                      }

                    }}
                    className="
                      mt-4 ml-auto block px-4 py-2
                      rounded-xl
                      bg-red-500/10
                      border border-red-500/20
                      text-red-300
                      hover:bg-red-500/20
                      transition-all duration-300
                    "
                  >
                    Delete
                  </button>

                </div>

              </div>

              <div className="mb-5">

                <h3 className="text-lg font-semibold mb-2 text-purple-300">
                  Candidate Skills
                </h3>

                <p className="text-gray-300">
                  {analysis.candidate_skills}
                </p>

              </div>

              <div>

                <h3 className="text-lg font-semibold mb-2 text-pink-300">
                  AI Summary
                </h3>

                <p className="text-gray-400 leading-8">
                  {analysis.ai_summary}
                </p>

              </div>

            </div>

          ))}

        </div>

      </div>

    </main>
  )
}
