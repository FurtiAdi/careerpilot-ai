"use client"

import { useState, useRef } from "react"

export default function Home() {

  // =========================
  // STATE VARIABLES
  // =========================

  // Stores job description text
  const [jobDescription, setJobDescription] = useState("")

  // Stores candidate skills input
  const [candidateSkills, setCandidateSkills] = useState("")

  // Controls loading spinner/button state
  const [loading, setLoading] = useState(false)

  // Stores analysis results returned from backend
  const [results, setResults] = useState<any>(null)

  // Reference used for auto-scrolling to results section
  const resultsRef = useRef<HTMLDivElement | null>(null)

  // Stores uploaded resume file
  const [resumeFile, setResumeFile] = useState<File | null>(null)

  // Stores extracted resume text
  const [resumeText, setResumeText] = useState("")


  // =========================
  // ANALYZE JOB FUNCTION
  // =========================

  const analyzeJob = async () => {

    // Enable loading state
    setLoading(true)

    try {

      // Convert comma-separated skills into array
      const skillsArray = candidateSkills
        .split(",")
        .map((skill) => skill.trim())

      // Send POST request to backend
      const response = await fetch(
        "http://127.0.0.1:8000/analyze-job",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          // Send job description and skills
          body: JSON.stringify({
            job_description: jobDescription,
            candidate_skills: skillsArray
          })
        }
      )

      // Convert backend response to JSON
      const data = await response.json()

      // Debugging log
      console.log(data)

      // Save results into state
      setResults(data)

      // Smooth scroll to results section
      setTimeout(() => {

        resultsRef.current?.scrollIntoView({
          behavior: "smooth"
        })

      }, 200)

    } catch (error) {

      // Print errors in console
      console.error(error)

    } finally {

      // Disable loading state
      setLoading(false)

    }
  }


  // =========================
  // RESUME UPLOAD FUNCTION
  // =========================

  const uploadResume = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {

    // Get uploaded file
    const file = event.target.files?.[0]

    // Stop if no file selected
    if (!file) return

    // Save uploaded file
    setResumeFile(file)

    // Create form data object
    const formData = new FormData()

    // Append uploaded PDF file
    formData.append("file", file)

    try {

      // Send uploaded file to backend
      const response = await fetch(
        "http://127.0.0.1:8000/upload-resume",
        {
          method: "POST",
          body: formData
        }
      )

      // Convert backend response to JSON
      const data = await response.json()

      // Save extracted resume text
      setResumeText(data.extracted_text)

      // Automatically fill candidate skills
      setCandidateSkills(
        data.detected_skills.join(", ")
      )

    } catch (error) {

      // Print errors in console
      console.error(error)

    }
  }


  // =========================
  // UI / JSX
  // =========================

  return (

    <main className="min-h-screen bg-black text-white overflow-hidden">

      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-purple-900/20 via-black to-black" />

      {/* Main page container */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-16">


        {/* =========================
            HERO SECTION
        ========================= */}

        <div className="text-center mb-16">

          {/* Small badge */}
          <div className="inline-block px-4 py-2 rounded-full border border-purple-500/30 bg-purple-500/10 text-sm text-purple-300 mb-6">
            AI-Powered Career Assistant
          </div>

          {/* Main heading */}
          <h1 className="text-6xl font-bold leading-tight mb-6">

            Analyze Job Descriptions.
            <br />

            <span className="bg-gradient-to-r from-purple-400 to-pink-500 text-transparent bg-clip-text">
              Boost Your Career.
            </span>

          </h1>

          {/* Subtitle */}
          <p className="text-gray-400 text-xl max-w-3xl mx-auto">
            Get AI-powered insights on your resume match,
            missing skills, and personalized improvement tips.
          </p>

        </div>


        {/* =========================
            FEATURE CARDS
        ========================= */}

        <div className="grid md:grid-cols-3 gap-6 mb-14">

          {/* Match Score Card */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">

            <h3 className="text-xl font-semibold mb-2">
              Smart Match Score
            </h3>

            <p className="text-gray-400">
              See how well your skills match the job.
            </p>

          </div>

          {/* Missing Skills Card */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">

            <h3 className="text-xl font-semibold mb-2">
              Missing Skills
            </h3>

            <p className="text-gray-400">
              Identify skill gaps instantly.
            </p>

          </div>

          {/* AI Suggestions Card */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm">

            <h3 className="text-xl font-semibold mb-2">
              AI Suggestions
            </h3>

            <p className="text-gray-400">
              Improve your resume with AI insights.
            </p>

          </div>

        </div>


        {/* =========================
            FORM SECTION
        ========================= */}

        <div className="bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md shadow-2xl">


          {/* Resume Upload */}
          <label className="block text-lg font-semibold mb-3">
            Upload Resume (PDF)
          </label>

          <div className="mb-8">

            <input
              type="file"
              accept=".pdf"
              onChange={uploadResume}
              className="w-full bg-black/40 border border-white/10 rounded-2xl p-5 text-gray-400"
            />

          </div>


          {/* Job Description */}
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


          {/* Candidate Skills */}
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


          {/* Analyze Button */}
          <button
            onClick={analyzeJob}
            disabled={loading}
            className={`
              w-full p-5 rounded-2xl font-semibold text-lg
              bg-gradient-to-r from-purple-600 to-pink-500
              transition flex items-center justify-center gap-3
              ${loading
                ? "opacity-70 cursor-not-allowed"
                : "hover:opacity-90"
              }
            `}
          >

            {/* Loading State */}
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />

                <span>Analyzing...</span>
              </>
            ) : (
              "Analyze Job Match"
            )}

          </button>

        </div>


        {/* =========================
            RESULTS SECTION
        ========================= */}

        {results && (

          <div
            ref={resultsRef}
            className="mt-10 bg-white/5 border border-white/10 rounded-3xl p-8 backdrop-blur-md"
          >

            {/* Results Heading */}
            <h2 className="text-3xl font-bold mb-8">
              Analysis Results
            </h2>


            {/* =========================
                TOP RESULT CARDS
            ========================= */}

            <div className="grid md:grid-cols-2 gap-6 mb-8">


              {/* Match Score Card */}
              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-xl font-semibold mb-4">
                  Match Score
                </h3>

                <div className="space-y-5">

                  <div className="flex items-end justify-between">

                    <div>

                      <p className="text-gray-400 text-sm mb-2">
                        Resume Match
                      </p>

                      <h2 className="text-4xl font-bold text-white">
                        {results.match_analysis.match_score}%
                      </h2>

                    </div>

                    {/* AI Score Badge */}
                    <div className="text-sm text-purple-300 bg-purple-500/10 border border-purple-500/20 px-3 py-1 rounded-full">
                      AI Score
                    </div>

                  </div>


                  {/* Animated Progress Bar */}
                  <div className="w-full h-3 bg-white/10 rounded-full overflow-hidden shadow-inner">

                    <div
                      className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-1000"
                      style={{
                        width: `${results.match_analysis.match_score}%`
                      }}
                    />

                  </div>

                </div>

              </div>


              {/* Skills Found Card */}
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


            {/* =========================
                MATCHED / MISSING SKILLS
            ========================= */}

            <div className="grid md:grid-cols-2 gap-6 mb-8">


              {/* Matched Skills */}
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


              {/* Missing Skills */}
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


            {/* =========================
                AI ANALYSIS SECTION
            ========================= */}

            <div className="bg-gradient-to-br from-purple-500/3 to-pink-500/3 border border-white/10 rounded-2xl p-8">

              {/* AI Analysis Heading */}
              <h3 className="text-3xl font-bold mb-6 bg-gradient-to-r from-purple-300 to-pink-400 text-transparent bg-clip-text">
                AI Analysis
              </h3>

              {/* AI Badge */}
              <div className="inline-flex items-center gap-2 mb-6 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-sm">
                AI Generated Insights
              </div>

              {/* AI Generated Text */}
              <div className="space-y-10">

                {/* Summary Section */}
                <div>

                  <h4 className="text-2xl font-semibold mb-4 text-white">
                    Summary
                  </h4>

                  <p className="max-w-4xl text-gray-300 leading-9 text-lg">
                    {results.ai_analysis.summary}
                  </p>

                </div>


                {/* Strengths Section */}
                <div>

                  <h4 className="text-2xl font-semibold mb-4 text-green-400">
                    Strengths
                  </h4>

                  <div className="grid gap-4">

                    {results.ai_analysis.strengths.map(
                      (item: string) => (

                        <div
                          key={item}
                          className="bg-green-500/10 border border-green-500/20 rounded-2xl p-4 text-gray-200"
                        >
                          ✅ {item}
                        </div>

                      )
                    )}
                  </div>
                </div>


                {/* Missing Requirements Section */}
                <div>

                  <h4 className="text-2xl font-semibold mb-4 text-red-400">
                    Missing Requirements
                  </h4>

                  <div className="grid gap-4">

                    {results.ai_analysis.missing_requirements.map(
                      (item: string) => (

                        <div
                          key={item}
                          className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 text-gray-200"
                        >
                          ❌ {item}
                        </div>
                      )
                    )}
                  </div>
                </div>


                {/* Recommendations Section */}
                <div>

                  <h4 className="text-2xl font-semibold mb-4 text-purple-300">
                    Recommendations
                  </h4>

                  <div className="grid gap-4">

                    {results.ai_analysis.recommendations.map(
                      (item: string) => (

                        <div
                          key={item}
                          className="bg-purple-500/10 border border-purple-500/20 rounded-2xl p-4 text-gray-200"
                        >
                          💡 {item}
                        </div>

                      )
                    )}

                  </div>

                </div>

              </div>

            </div>

          </div>

        )}

      </div>
    </main>
  )
}