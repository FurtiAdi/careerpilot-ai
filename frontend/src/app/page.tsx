"use client"
import { useState, useRef } from "react"

export default function Home() {
  const [jobDescription, setJobDescription] = useState("")
  const [candidateSkills, setCandidateSkills] = useState("")
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const resultsRef = useRef<HTMLDivElement | null>(null)

    const analyzeJob = async () => {

    setLoading(true)

    try {

      const skillsArray = candidateSkills
        .split(",")
        .map((skill) => skill.trim())

      const response = await fetch(
        "http://127.0.0.1:8000/analyze-job",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            job_description: jobDescription,
            candidate_skills: skillsArray
          })
        }
      )

      const data = await response.json()
      console.log(data)
      setResults(data)

      setTimeout(() => {

        resultsRef.current?.scrollIntoView({
          behavior: "smooth"
        })

      }, 200)

    } catch (error) {

      console.error(error)

    } finally {

      setLoading(false)

    }
  }

  return (
    <main className="min-h-screen bg-black text-white overflow-hidden">

      <div className="absolute inset-0 bg-gradient-to-b from-purple-900/20 via-black to-black" />

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">

        <div className="text-center mb-16">

          <div className="inline-block px-4 py-2 rounded-full border border-purple-500/30 bg-purple-500/10 text-sm text-purple-300 mb-6">
            AI-Powered Career Assistant
          </div>

          <h1 className="text-6xl font-bold leading-tight mb-6">

            Analyze Job Descriptions.
            <br />

            <span className="bg-gradient-to-r from-purple-400 to-pink-500 text-transparent bg-clip-text">
              Boost Your Career.
            </span>

          </h1>

          <p className="text-gray-400 text-xl max-w-3xl mx-auto">
            Get AI-powered insights on your resume match,
            missing skills, and personalized improvement tips.
          </p>

        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-14">

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h3 className="text-xl font-semibold mb-2">
              Smart Match Score
            </h3>

            <p className="text-gray-400">
              See how well your skills match the job.
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h3 className="text-xl font-semibold mb-2">
              Missing Skills
            </h3>

            <p className="text-gray-400">
              Identify skill gaps instantly.
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">
            <h3 className="text-xl font-semibold mb-2">
              AI Suggestions
            </h3>

            <p className="text-gray-400">
              Improve your resume with AI insights.
            </p>
          </div>

        </div>

        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md shadow-2xl">

          <label className="block text-lg font-semibold mb-3">
            Job Description
          </label>

          <textarea
            value={jobDescription}
            onChange={(event) =>
              setJobDescription(event.target.value)
            }
            className="w-full h-56 bg-black/40 border border-white/10 rounded-2xl p-5 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 mb-8"
            placeholder="Paste job description here..."
          />

          <label className="block text-lg font-semibold mb-3">
            Candidate Skills
          </label>

          <input
            type="text"
            value={candidateSkills}
            onChange={(event) =>
              setCandidateSkills(event.target.value)
            }
            className="w-full bg-black/40 border border-white/10 rounded-2xl p-5 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 mb-8"
            placeholder="Example: Python, React, SQL, AWS"
          />

          <button
            onClick={analyzeJob}
            className="w-full p-5 rounded-2xl font-semibold text-lg bg-gradient-to-r from-purple-600 to-pink-500 hover:opacity-90 transition"
          >
            Analyze Job Match
          </button>

        </div>
                {results && (

            <div ref={resultsRef} className="mt-10 bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md" >

            <h2 className="text-3xl font-bold mb-8">
              Analysis Results
            </h2>

            <div className="grid md:grid-cols-2 gap-6 mb-8">

              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-xl font-semibold mb-4">
                  Match Score
                </h3>

                <div className="text-5xl font-bold text-purple-400">
                  {results.match_analysis.match_score}%
                </div>

              </div>

              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-xl font-semibold mb-4">
                  Skills Found
                </h3>

                <div className="flex flex-wrap gap-2">

                  {results.detected_job_skills.map(
                    (skill: string) => (

                      <span
                        key={skill}
                        className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-sm"
                      >
                        {skill}
                      </span>
                    )
                  )}

                </div>

              </div>

            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">

              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-xl font-semibold mb-4 text-green-400">
                  Matched Skills
                </h3>

                <ul className="space-y-2">

                  {results.match_analysis.matched_skills.map(
                    (skill: string) => (

                      <li key={skill}>
                        ✅ {skill}
                      </li>
                    )
                  )}

                </ul>

              </div>

              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-xl font-semibold mb-4 text-red-400">
                  Missing Skills
                </h3>

                <ul className="space-y-2">

                  {results.match_analysis.missing_skills.map(
                    (skill: string) => (

                      <li key={skill}>
                        ❌ {skill}
                      </li>
                    )
                  )}

                </ul>

              </div>

            </div>

            <div className="bg-black/30 rounded-2xl p-6">

              <h3 className="text-2xl font-semibold mb-4">
                AI Analysis
              </h3>

              <p className="text-gray-300 whitespace-pre-line leading-8">
                {results.ai_analysis}
              </p>

            </div>

          </div>

        )}

      </div>
      

    </main>
  )
}