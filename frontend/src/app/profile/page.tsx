"use client"

import { useEffect, useState } from "react"

export default function ProfilePage() {

  const [user, setUser] = useState<any>(null)

  useEffect(() => {

    fetchProfile()

  }, [])

  const fetchProfile = async () => {

    try {

      const token = localStorage.getItem(
        "token"
      )

      const response = await fetch(
        "http://127.0.0.1:8000/me",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      const data = await response.json()

      setUser(data)

    } catch (error) {

      console.error(error)

    }

  }

  return (

    <main className="min-h-screen bg-black text-white pt-32 px-6 pb-20 overflow-hidden">

      {/* Purple Glow */}
      <div className="absolute top-32 left-10 w-72 h-72 bg-purple-600/20 blur-[120px] rounded-full" />

      {/* Pink Glow */}
      <div className="absolute bottom-20 right-10 w-72 h-72 bg-pink-600/20 blur-[120px] rounded-full" />

      <div className="relative z-10 max-w-6xl mx-auto">

        {/* Heading */}
        <h1
          className="
            text-5xl font-bold mb-12
            bg-gradient-to-r
            from-purple-400
            to-pink-500
            text-transparent bg-clip-text
          "
        >
          My Profile
        </h1>

        {/* Main Profile Card */}
        <div
          className="
            bg-white/5
            border border-white/10
            rounded-[32px]
            p-10
            backdrop-blur-xl
          "
        >

          <div className="flex flex-col lg:flex-row gap-10 items-start">

            {/* LEFT SIDE */}
            <div className="flex flex-col items-center">

              {/* Avatar */}
              <div
                className="
                  w-40 h-40 rounded-full
                  bg-gradient-to-r
                  from-purple-500
                  to-pink-500
                  flex items-center justify-center
                  text-5xl font-bold
                  shadow-2xl shadow-pink-500/20
                "
              >

                {user?.full_name
                  ?.split(" ")
                  .map((name: string) =>
                    name.charAt(0)
                  )
                  .join("")
                  .slice(0, 2)}

              </div>

              {/* Upload Button */}
              <button
                className="
                  mt-6 px-6 py-3 rounded-2xl
                  bg-white/5
                  border border-white/10
                  hover:border-purple-500/40
                  transition-all duration-300
                "
              >
                Change Photo
              </button>

            </div>

            {/* RIGHT SIDE */}
            <div className="flex-1 w-full">

              {/* Name */}
              <div className="mb-8">

                <p className="text-sm text-gray-500 mb-2">
                  Full Name
                </p>

                <h2 className="text-4xl font-bold">
                  {user?.full_name}
                </h2>

              </div>

              {/* Email */}
              <div className="mb-8">

                <p className="text-sm text-gray-500 mb-2">
                  Email Address
                </p>

                <p className="text-xl text-gray-300">
                  {user?.email}
                </p>

              </div>

              {/* Stats */}
              <div className="grid md:grid-cols-3 gap-6">

                {/* Analyses */}
                <div
                  className="
                    bg-black/30
                    border border-white/10
                    rounded-3xl
                    p-6
                  "
                >

                  <p className="text-gray-500 mb-3">
                    Analyses
                  </p>

                  <h3 className="text-4xl font-bold text-purple-300">
                    12
                  </h3>

                </div>

                {/* Match Rate */}
                <div
                  className="
                    bg-black/30
                    border border-white/10
                    rounded-3xl
                    p-6
                  "
                >

                  <p className="text-gray-500 mb-3">
                    Avg Match
                  </p>

                  <h3 className="text-4xl font-bold text-pink-300">
                    82%
                  </h3>

                </div>

                {/* Resume */}
                <div
                  className="
                    bg-black/30
                    border border-white/10
                    rounded-3xl
                    p-6
                  "
                >

                  <p className="text-gray-500 mb-3">
                    Resume
                  </p>

                  <h3 className="text-xl font-semibold text-green-300">
                    Uploaded
                  </h3>

                </div>

              </div>

            </div>

          </div>

        </div>

      </div>

    </main>
  )
}
