"use client"

import Link from "next/link"

import ApplicationCreationForm from "@/components/applications/ApplicationCreationForm"

export default function NewApplicationPage() {
  return (
    <main className="min-h-screen bg-black px-6 py-28 text-white">
      <div className="mx-auto max-w-4xl">
        <div className="mb-10 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm text-purple-300">
              Application Tracker
            </p>

            <h1 className="mt-2 text-4xl font-bold">
              Track an application
            </h1>

            <p className="mt-2 text-gray-400">
              Save the application details, dates, notes, and related
              CareerPilot documents you want to follow.
            </p>
          </div>

          <Link
            href="/applications"
            className="rounded-xl border border-purple-500/40 px-4 py-2 font-semibold text-purple-200 hover:bg-purple-500/10"
          >
            Back to applications
          </Link>
        </div>

        <section className="rounded-3xl border border-purple-500/20 bg-purple-500/10 p-6">
          <ApplicationCreationForm />
        </section>
      </div>
    </main>
  )
}
