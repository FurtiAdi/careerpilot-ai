"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { type FormEvent, useState } from "react"
import {
  ArrowRight,
  Lock,
  Mail,
  User,
} from "lucide-react"

import { register } from "@/services/authService"

export default function RegisterPage() {
  const router = useRouter()

  const [fullName, setFullName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [loading, setLoading] = useState(false)

  const registerUser = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault()

    if (
      !fullName.trim() ||
      !email.trim() ||
      !password ||
      !confirmPassword
    ) {
      alert("Please fill in all fields.")
      return
    }

    if (password !== confirmPassword) {
      alert("Passwords do not match.")
      return
    }

    try {
      setLoading(true)

      await register({
        fullName: fullName.trim(),
        email: email.trim(),
        password,
      })

      alert("Account created successfully. Please log in.")

      router.push("/login")
    } catch (error) {
      console.error(error)

      if (error instanceof Error) {
        alert(error.message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 px-6 pb-12 pt-28 text-slate-900">
      <div className="pointer-events-none absolute left-0 top-20 h-72 w-72 rounded-full bg-purple-200/50 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-80 w-80 rounded-full bg-pink-100/70 blur-3xl" />

      <section className="relative mx-auto flex min-h-[calc(100vh-10rem)] max-w-md items-center">
        <div className="w-full rounded-3xl border border-slate-200 bg-white p-8 shadow-xl shadow-purple-950/10 sm:p-10">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-purple-600 to-pink-500 text-white shadow-lg shadow-purple-500/30">
              <User className="h-6 w-6" />
            </div>

            <p className="mb-2 text-sm font-semibold text-purple-600">
              CareerPilot AI
            </p>

            <h1 className="text-3xl font-bold tracking-tight text-slate-950">
              Create your account
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-600">
              Start your focused job-search journey with CareerPilot.
            </p>
          </div>

          <form
            onSubmit={registerUser}
            className="space-y-5"
          >
            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-800">
                Full name
              </span>

              <div className="relative">
                <User className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />

                <input
                  type="text"
                  value={fullName}
                  onChange={(event) =>
                    setFullName(event.target.value)
                  }
                  placeholder="Alex Johnson"
                  autoComplete="name"
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white pl-12 pr-4 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-purple-500 focus:ring-4 focus:ring-purple-100"
                />
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-800">
                Email
              </span>

              <div className="relative">
                <Mail className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />

                <input
                  type="email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  placeholder="name@example.com"
                  autoComplete="email"
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white pl-12 pr-4 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-purple-500 focus:ring-4 focus:ring-purple-100"
                />
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-800">
                Password
              </span>

              <div className="relative">
                <Lock className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />

                <input
                  type="password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  placeholder="Create a password"
                  autoComplete="new-password"
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white pl-12 pr-4 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-purple-500 focus:ring-4 focus:ring-purple-100"
                />
              </div>
            </label>

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-800">
                Confirm password
              </span>

              <div className="relative">
                <Lock className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />

                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(event.target.value)
                  }
                  placeholder="Repeat your password"
                  autoComplete="new-password"
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white pl-12 pr-4 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-purple-500 focus:ring-4 focus:ring-purple-100"
                />
              </div>
            </label>

            <button
              type="submit"
              disabled={loading}
              className="flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 font-semibold text-white shadow-lg shadow-purple-500/25 transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading
                ? "Creating account..."
                : "Create account"}

              {!loading && (
                <ArrowRight className="h-5 w-5" />
              )}
            </button>
          </form>

          <p className="mt-7 text-center text-sm text-slate-600">
            Already have an account?{" "}

            <Link
              href="/login"
              className="font-semibold text-purple-700 transition hover:text-pink-600"
            >
              Log in
            </Link>
          </p>
        </div>
      </section>
    </main>
  )
}
