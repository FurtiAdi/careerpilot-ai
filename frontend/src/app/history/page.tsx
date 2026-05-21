"use client"

import { useEffect, useState } from "react"

export default function HistoryPage() {

  const [analyses, setAnalyses] = useState<any[]>([])

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

  return (

    <main className="min-h-screen bg-black text-white p-10">

      <div className="max-w-6xl mx-auto">

        <h1 className="text-5xl font-bold mb-10 bg-gradient-to-r from-purple-400 to-pink-500 text-transparent bg-clip-text">
          Analysis History
        </h1>

        <div className="grid gap-6">

          {analyses.map((analysis) => (

            <div
              key={analysis.id}
              className="bg-white/5 border border-white/10 rounded-3xl p-8"
            >

              <div className="flex items-center justify-between mb-6">

                <h2 className="text-2xl font-semibold">
                  Analysis #{analysis.id}
                </h2>

                <div className="text-3xl font-bold text-purple-400">
                  {analysis.match_score}%
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