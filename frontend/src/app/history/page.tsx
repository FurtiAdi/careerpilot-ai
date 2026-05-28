"use client"

import { useEffect, useState } from "react"

type Analysis = {
  id: number
  job_description: string
  candidate_skills: string
  match_score: number
  ai_summary: string
  created_at: string
}

export default function HistoryPage() {

  const [analyses, setAnalyses] = useState<Analysis[]>([])

  useEffect(() => {

    fetchAnalyses()

  }, [])

  const fetchAnalyses = async () => {

    try {

      const response = await fetch(
        "http://127.0.0.1:8000/analyses"
      )

      const data = await response.json()

      setAnalyses(data)

    } catch (error) {

      console.error(error)

    }
  }

  const deleteAnalysis = async (
    id: number
  ) => {

    try {

      await fetch(
        `http://127.0.0.1:8000/analyses/${id}`,
        {
          method: "DELETE"
        }
      )

      setAnalyses((prev) =>
        prev.filter(
          (analysis) =>
            analysis.id !== id
        )
      )

    } catch (error) {

      console.error(error)

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

    <main className="min-h-screen bg-black text-white px-10 py-16">

      <div className="max-w-5xl mx-auto">

        <h1 className="text-4xl font-bold mb-10 bg-gradient-to-r from-purple-400 to-pink-500 text-transparent bg-clip-text">
          Analysis History
        </h1>

        <div className="grid gap-6">

          {analyses.length === 0 && (

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
                    onClick={() =>
                      deleteAnalysis(analysis.id)
                    }
                    className="
                      mt-4 px-4 py-2
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