"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/dist/client/link"

export default function LoginPage() {

    const [email, setEmail] = useState("")

    const [password, setPassword] = useState("")

    const [loading, setLoading] = useState(false)

    const router = useRouter()

    const loginUser = async () => {

    try {

      setLoading(true)

      const response = await fetch(
        "http://127.0.0.1:8000/login",
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

      if (data.access_token) {

        localStorage.setItem(
          "token",
          data.access_token
        )

        window.location.href = "/"

      } else {

        alert(data.error)

      }

    } catch (error) {

      console.error(error)

    } finally {

      setLoading(false)

    }

  }

  return (

    <main
        className="
            min-h-screen
            bg-black text-white
            flex items-center justify-center
            px-6 py-10
            "
    >
      <div
        className="
          w-full max-w-md
          bg-white/5
          border border-white/10
          rounded-3xl
          p-8
          backdrop-blur-xl
        "
      >

        <h1
          className="
            text-4xl font-bold mb-8 text-center
            bg-gradient-to-r from-purple-400 to-pink-500
            text-transparent bg-clip-text
          "
        >
          Login
        </h1>

        <div className="space-y-6">

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(event) =>
              setEmail(event.target.value)
            }
            className="
              w-full p-4 rounded-2xl
              bg-black/40
              border border-white/10
              focus:outline-none
              focus:border-purple-500
            "
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(event) =>
              setPassword(event.target.value)
            }
            className="
              w-full p-4 rounded-2xl
              bg-black/40
              border border-white/10
              focus:outline-none
              focus:border-purple-500
            "
          />

          <button
            onClick={loginUser}
            disabled={loading}
            className="
              w-full p-4 rounded-2xl
              bg-gradient-to-r
              from-purple-600
              to-pink-500
              font-semibold
              transition-all
              hover:opacity-90
            "
          >
            {loading
              ? "Logging in..."
              : "Login"}
          </button>

        </div>

        <p className="text-center text-gray-400 mt-6">

            Don't have an account?

            <Link
                href="/register"
                className="
                ml-2 text-purple-400
                hover:text-pink-400
                "
            >
                Register
            </Link>

            </p>

      </div>

    </main>
  )
}