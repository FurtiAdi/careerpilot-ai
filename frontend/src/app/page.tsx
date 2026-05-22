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

    // Validation
    if (!jobDescription.trim()) {
      alert("Please enter a job description.")
      return
    }

    if (!candidateSkills.trim()) {
      alert("Please enter your skills.")
      return
    }

    if (!resumeFile) {
      alert("Please upload your resume.")
      return
    }

    try {
      // Enable loading state      
      setLoading(true)

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

      {/* Purple glow background */}
      <div className="absolute top-40 left-10 w-72 h-72 bg-purple-600/20 blur-[120px] rounded-full" />

      {/* Pink glow background */}
      <div className="absolute top-96 right-10 w-72 h-72 bg-pink-600/20 blur-[120px] rounded-full" />
      
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#120018] via-black to-black" />
      
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
          <h1
            className="
              text-5xl font-bold
              leading-[1.1]
              mb-6
              max-w-5xl
              mx-auto
            "
          >

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

          <h2 className="text-2xl font-semibold mb-6">
            Upload Resume
          </h2>
          {/* Resume Upload */}
          <div className="mb-8">

            <label
              className="
                flex items-center justify-center
                w-full h-24
                border border-white/10
                rounded-2xl
                bg-black/40
                hover:border-purple-400
                hover:bg-purple-500/5
                transition-all duration-300
                cursor-pointer
              "
            >

              <div className="text-center">

                <p className="text-lg font-medium text-white">
                  Upload Resume
                </p>

                <p className="text-sm text-gray-500 mt-1">
                  PDF files only
                </p>

                {resumeFile && (
                  <p className="mt-2 text-purple-300 text-sm">
                    {resumeFile.name}
                  </p>
                )}

              </div>

              <input
                type="file"
                accept=".pdf"
                onChange={uploadResume}
                className="hidden"
              />

            </label>

          </div>


          {/* Job Description */}
          <label className="block text-lg font-semibold mb-3 text-gray-100">
            Job Description
          </label>

          <textarea
            value={jobDescription}
            onChange={(event) =>
              setJobDescription(event.target.value)
            }
            className="
              w-full h-44 bg-black/40 border border-white/10 rounded-2xl p-5 text-white placeholder:text-gray-500
              focus:outline-none 
              focus:border-purple-500
              focus:ring-2
              focus:ring-purple-500/20 mb-8
            "
            placeholder="Paste job description here..."
          />


          {/* Candidate Skills */}
          <label className="block text-lg font-semibold mb-3 text-gray-100">
            Candidate Skills
          </label>

          <input
            type="text"
            value={candidateSkills}
            onChange={(event) =>
              setCandidateSkills(event.target.value)
            }
            className="w-full bg-black/40 border border-white/10 rounded-2xl p-5 text-white placeholder:text-gray-500 focus:outline-none focus:border-purple-500 mb-8"
            placeholder="Example: Python, React, SQL, AWS"
          />


          {/* Analyze Button */}
          <button
            onClick={analyzeJob}
            disabled={loading}
            className={`
              w-full p-5 rounded-2xl font-semibold text-lg
              bg-gradient-to-r 
              from-purple-600 
              to-pink-500
              flex items-center 
              justify-center gap-3
              shadow-lg shadow-pink-500/20
              transition-all duration-300
              ${loading
                ? "opacity-70 cursor-not-allowed"
                : `
                  hover:opacity-95
                  hover:scale-[1.01]
                  hover:shadow-pink-500/40
                  active:scale-[0.99]
                `
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

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 gap-6 mb-8">


              {/* Match Score Card */}
              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
                  📊 Match Score
                </h3>

                <div className="flex flex-col items-center justify-center">

                  {/* Circle Container */}
                  <div className="relative w-52 h-52">

                    {/* Background Circle */}
                    <svg
                      className="w-full h-full rotate-[-90deg]"
                      viewBox="0 0 200 200"
                    >

                      <circle
                        cx="100"
                        cy="100"
                        r="85"
                        stroke="rgba(255,255,255,0.08)"
                        strokeWidth="14"
                        fill="none"
                      />

                      {/* Progress Circle */}
                      <circle
                        cx="100"
                        cy="100"
                        r="85"
                        stroke="url(#gradient)"
                        strokeWidth="14"
                        fill="none"
                        strokeLinecap="round"
                        strokeDasharray={534}
                        strokeDashoffset={
                          534 -
                          (534 *
                            results.match_analysis.match_score) /
                            100
                        }
                        className="
                          transition-all
                          duration-[2000ms]
                          ease-out
                        "
                      />

                      {/* Gradient */}
                      <defs>

                        <linearGradient
                          id="gradient"
                          x1="0%"
                          y1="0%"
                          x2="100%"
                          y2="100%"
                        >

                          <stop
                            offset="0%"
                            stopColor="#a855f7"
                          />

                          <stop
                            offset="100%"
                            stopColor="#ec4899"
                          />

                        </linearGradient>

                      </defs>

                    </svg>

                    {/* Center Score */}
                    <div
                      className="
                        absolute inset-0
                        flex flex-col
                        items-center justify-center
                      "
                    >

                      <p className="text-gray-400 text-sm mb-2">
                        Match Score
                      </p>

                      <h2
                        className="
                          text-5xl font-bold
                          bg-gradient-to-r
                          from-purple-300
                          to-pink-400
                          text-transparent bg-clip-text
                        "
                      >
                        {results.match_analysis.match_score}%
                      </h2>

                    </div>

                  </div>

                </div>

              </div>

            </div>


            {/* =========================
                MATCHED / MISSING SKILLS
            ========================= */}

            <div className="grid md:grid-cols-2 gap-6 mb-8">


              {/* Matched Skills */}
              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-xl font-bold mb-6 text-green-400">
                    ✅ Matched Skills
                </h3>

                <div className="flex flex-wrap gap-3">

                  {results.match_analysis.matched_skills.length > 0 ? (
                    results.match_analysis.matched_skills.map(
                    (skill: string) => (

                      <div
                        key={skill}
                        className="
                          px-4 py-2 rounded-full
                          bg-green-500/10
                          border border-green-500/20
                          text-green-300
                          text-sm font-medium
                        "
                      >
                        {skill}
                      </div>

                    )
                  )) : (

                    <p className="text-gray-500">
                      No matched skills found.
                    </p>

                  )}

                </div>

              </div>


              {/* Missing Skills */}
              <div className="bg-black/30 rounded-2xl p-6">

                <h3 className="text-xl font-bold mb-6 text-red-400">
                  ❌ Missing Skills
                </h3>

                <div className="flex flex-wrap gap-3">

                  {results.match_analysis.missing_skills.map(
                    (skill: string) => (
                      <div
                        key={skill}
                        className="
                          px-4 py-2 rounded-full
                          bg-red-500/10
                          border border-red-500/20
                          text-red-300
                          text-sm font-medium
                        "
                      >
                        {skill}
                      </div>

                    )
                  )}

                </div>

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