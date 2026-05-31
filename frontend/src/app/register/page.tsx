"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import {
  User,
  Mail,
  Lock,
  FileText
} from "lucide-react"

export default function RegisterPage() {

  const router = useRouter()

  const [fullName, setFullName] =
    useState("")

  const [email, setEmail] =
    useState("")

  const [password, setPassword] =
    useState("")

  const [profileImage, setProfileImage] =
    useState<File | null>(null)

  const [resumeFile, setResumeFile] =
    useState<File | null>(null)

  const [loading, setLoading] =
    useState(false)

  const registerUser = async () => {

    if (
      !fullName ||
      !email ||
      !password
    ) {

      alert("Please fill all fields")

      return
    }

    try {

      setLoading(true)

      const response = await fetch(
        "http://127.0.0.1:8000/register",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({

            full_name: fullName,

            email,

            password
          })
        }
      )

      const data = await response.json()

      if (data.error) {

        alert(data.error)

        return
      }

      alert("Account created successfully!")

      router.push("/login")

    } catch (error) {

      console.error(error)

    } finally {

      setLoading(false)

    }

  }

  return (

    <main className="min-h-screen bg-black text-white flex items-center justify-center px-6 py-20 overflow-x-hidden">

      {/* Purple Glow */}
      <div className="absolute top-40 left-10 w-72 h-72 bg-purple-600/20 blur-[120px] rounded-full" />

      {/* Pink Glow */}
      <div className="absolute bottom-20 right-10 w-72 h-72 bg-pink-600/20 blur-[120px] rounded-full" />

      <div
        className="
          relative z-10
          w-full max-w-lg
          bg-white/5
          border border-white/10
          rounded-3xl
          p-8
          backdrop-blur-xl
        "
      >

        {/* Heading */}
        <h1
          className="
            text-3xl font-bold text-center mb-4
            bg-gradient-to-r
            from-purple-400
            to-pink-500
            text-transparent bg-clip-text
          "
        >
          Create Profile
        </h1>

        <p className="text-center text-gray-400 mb-5">
            Start your AI-powered career journey
        </p>

        {/* Profile Picture Upload */}
        <div className="flex flex-col items-center mb-5">

        <label className="relative cursor-pointer group">

            {/* Avatar Circle */}
            <div
            className="
                w-24 h-24 rounded-full
                bg-gradient-to-br
                from-white/10
                to-white/5
                border border-white/10
                overflow-hidden
                flex items-center justify-center
                transition-all duration-300
                group-hover:scale-105
                group-hover:border-purple-400
            "
            >

            {profileImage ? (

                <img
                src={URL.createObjectURL(profileImage)}
                alt="Profile"
                className="w-full h-full object-cover"
                />

            ) : (

                <svg
                xmlns="http://www.w3.org/2000/svg"
                className="w-16 h-16 text-gray-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                >

                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M15.75 6.75a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.5 20.118a7.5 7.5 0 0115 0A17.933 17.933 0 0112 21.75a17.933 17.933 0 01-7.5-1.632z"
                />

                </svg>

            )}

            </div>

            {/* Plus Icon */}
            <div
            className="
                absolute bottom-1 right-1
                w-8 h-8 rounded-full
                bg-gradient-to-r
                from-purple-500
                to-pink-500
                flex items-center justify-center
                shadow-lg shadow-pink-500/30
                border-4 border-black
            "
            >

            <span className="text-white text-2xl leading-none">
                +
            </span>

            </div>

            {/* Hidden Input */}
            <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) =>
                setProfileImage(
                e.target.files?.[0] || null
                )
            }
            />

        </label>

        </div>

        {/* Full Name */}
        <div className="mb-5">

            <label className="block mb-2 text-gray-300">
                Full Name
            </label>

            <div className="relative">

                <input
                type="text"
                placeholder="Your name"
                value={fullName}
                onChange={(e) =>
                    setFullName(e.target.value)
                }
                className="
                    w-full h-14
                    bg-black/40
                    border border-white/10
                    rounded-2xl
                    px-5 pr-14
                    text-white
                    placeholder:text-gray-500
                    focus:outline-none
                    focus:border-purple-500
                "
                />

                <User
                className="
                    absolute right-5 top-1/2
                    -translate-y-1/2
                    text-gray-500
                    w-5 h-5
                "
                />

            </div>
        </div>

        {/* Email */}
        <div className="mb-5">

            <label className="block mb-2 text-gray-300">
                Email
            </label>

            <div className="relative">

                <input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) =>
                    setEmail(e.target.value)
                }
                className="
                    w-full h-14
                    bg-black/40
                    border border-white/10
                    rounded-2xl
                    px-5 pr-14
                    text-white
                    placeholder:text-gray-500
                    focus:outline-none
                    focus:border-purple-500
                "
                />

                <Mail
                className="
                    absolute right-5 top-1/2
                    -translate-y-1/2
                    text-gray-500
                    w-5 h-5
                "
                />

            </div>

        </div>

        {/* Password */}
        <div className="mb-5">

            <label className="block mb-2 text-gray-300">
                Password
            </label>

            <div className="relative">

                <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) =>
                    setPassword(e.target.value)
                }
                className="
                    w-full h-14
                    bg-black/40
                    border border-white/10
                    rounded-2xl
                    px-5 pr-14
                    text-white
                    placeholder:text-gray-500
                    focus:outline-none
                    focus:border-purple-500
                "
                />

                <Lock
                className="
                    absolute right-5 top-1/2
                    -translate-y-1/2
                    text-gray-500
                    w-5 h-5
                "
                />

            </div>

        </div>

        {/* CV Upload */}
        <div className="mb-5">

          <label className="block mb-2 text-gray-300">
            Upload CV (Optional)
          </label>

          <label
            className="
              flex items-center justify-center
              w-full h-16
              rounded-2xl
              border border-dashed border-pink-500/30
              bg-black/40
              cursor-pointer
              hover:border-pink-400
              transition-all duration-300
            "
          >

            <div className="text-center">

              <div className="flex items-center gap-3 text-white">

                    <FileText className="w-5 h-5 text-pink-400" />

                    <p>
                        Upload Resume
                    </p>

                </div>

                {resumeFile && (
                    <p className="text-sm text-pink-300 mt-2">
                    {resumeFile.name}
                    </p>
              )}

            </div>

            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) =>
                setResumeFile(
                  e.target.files?.[0] || null
                )
              }
            />

          </label>

        </div>

        {/* Register Button */}
        <button
          onClick={registerUser}
          disabled={loading}
          className="
            w-full h-14 rounded-2xl
            bg-gradient-to-r
            from-purple-600
            to-pink-500
            font-semibold text-lg
            hover:opacity-90
            transition-all duration-300
          "
        >

          {loading
            ? "Creating Profile..."
            : "Create Account"
          }

        </button>

        {/* Login Link */}
        <p className="text-center text-gray-400 mt-8">

          Already have an account?

          <Link
            href="/login"
            className="
              ml-2 text-purple-400
              hover:text-pink-400
            "
          >
            Sign In
          </Link>

        </p>

      </div>

    </main>
  )
}
