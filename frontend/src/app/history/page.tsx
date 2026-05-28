"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

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
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {

    const token = localStorage.getItem(
      "token"
    )

    if (!token) {

      router.push("/login")

      return
    }

    fetchAnalyses()

  }, [])

  const fetchAnalyses = async () => {

    try {

      const token = localStorage.getItem(
        "token"
      )

      const response = await fetch(
        "http://127.0.0.1:8000/analyses",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      
      if (response.status === 401) {

        localStorage.removeItem("token")

        router.push("/login")

        return
      }

      const data = await response.json()

      setAnalyses(data)
      setLoading(false)

    } catch (error) {

      console.error(error)
      setLoading(false)

    }
  }

  const deleteAnalysis = async (
    id: number
  ) => {

    try {

      const token = localStorage.getItem(
        "token"
      )

      await fetch(
        `http://127.0.0.1:8000/analyses/${id}`,
        {
          method: "DELETE",

          headers: {
            Authorization: `Bearer ${token}`
          }
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

    <main className="min-h-screen pt-28 bg-black text-white px-10 py-16">

      <div className="max-w-5xl mx-auto">

        <h1 className="text-4xl font-bold mb-10 bg-gradient-to-r from-purple-400 to-pink-500 text-transparent bg-clip-text">
          Analysis History
        </h1>

        <div className="grid gap-6">

          {loading && (

            <div className="text-center py-20">

              <div className="inline-block w-10 h-10 border-4 border-purple-500/20 border-t-purple-400 rounded-full animate-spin" />

            </div>

          )}

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
                    onClick={() => {

                      const confirmed = confirm(
                        "Delete this analysis?"
                      )

                      if (confirmed) {
                        deleteAnalysis(analysis.id)
                      }

                    }}
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