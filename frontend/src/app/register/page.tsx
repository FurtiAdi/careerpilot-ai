"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"

export default function RegisterPage() {

  const router = useRouter()

  const [email, setEmail] = useState("")

  const [password, setPassword] =
    useState("")

  const [loading, setLoading] =
    useState(false)

  const registerUser = async () => {

    if (!email || !password) {

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

    <main className="min-h-screen bg-black text-white flex items-center justify-center px-6">

      <div
        className="
          w-full max-w-md
          bg-white/5
          border border-white/10
          rounded-3xl
          p-10
          backdrop-blur-xl
        "
      >

        <h1
          className="
            text-4xl font-bold mb-8 text-center
            bg-gradient-to-r
            from-purple-400
            to-pink-500
            text-transparent bg-clip-text
          "
        >
          Create Account
        </h1>

        {/* Email */}
        <div className="mb-6">

          <label className="block mb-2 text-gray-300">
            Email
          </label>

          <input
            type="email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            className="
              w-full p-4 rounded-2xl
              bg-black/40
              border border-white/10
              text-white
              focus:outline-none
              focus:border-purple-500
            "
            placeholder="Enter your email"
          />

        </div>

        {/* Password */}
        <div className="mb-8">

          <label className="block mb-2 text-gray-300">
            Password
          </label>

          <input
            type="password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            className="
              w-full p-4 rounded-2xl
              bg-black/40
              border border-white/10
              text-white
              focus:outline-none
              focus:border-purple-500
            "
            placeholder="Enter your password"
          />

        </div>

        {/* Register Button */}
        <button
          onClick={registerUser}
          disabled={loading}
          className="
            w-full p-4 rounded-2xl
            bg-gradient-to-r
            from-purple-600
            to-pink-500
            font-semibold
            hover:opacity-90
            transition-all duration-300
          "
        >

          {loading
            ? "Creating Account..."
            : "Register"
          }

        </button>

        {/* Login Link */}
        <p className="text-center text-gray-400 mt-6">

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

