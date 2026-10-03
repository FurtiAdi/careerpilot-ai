"use client"

import { useEffect, useState } from "react"

import Link from "next/link"
import { useRouter } from "next/navigation"

import {
  getApplications,
  type Application,
  type ApplicationStatus,
} from "@/services/applicationService"

const applicationStatuses: ApplicationStatus[] = [
  "saved",
  "applied",
  "screening",
  "interview",
  "offer",
  "rejected",
  "withdrawn",
]

function formatStatus(status: ApplicationStatus): string {
  return status.charAt(0).toUpperCase() + status.slice(1)
}

function formatDate(value: string | null): string {
  if (!value) {
    return "Not set"
  }

  return new Date(`${value}T00:00:00`).toLocaleDateString()
}

export default function ApplicationsPage() {
    const router = useRouter()
    const [applications, setApplications] = useState<
        Application[]
    >([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [statusFilter, setStatusFilter] = useState<
        ApplicationStatus | "all"
    >("all")
    const [companyFilter, setCompanyFilter] = useState("all")
    const [roleFilter, setRoleFilter] = useState("all")
    const [appliedDateFilter, setAppliedDateFilter] =
        useState("")

    useEffect(() => {
        const token = localStorage.getItem("token")

        if (!token) {
        router.push("/login")
        return
        }

        let cancelled = false

        const loadApplications = async () => {
            try {
                setError(null)

                const applicationData = await getApplications()

                if (!cancelled) {
                    setApplications(applicationData)
                }
            } catch (error) {
                if (!cancelled) {
                setError(
                    error instanceof Error
                    ? error.message
                    : "Failed to load applications."
                )
                }
            } finally {
                if (!cancelled) {
                setLoading(false)
                }
            }
        }

        void loadApplications()

        return () => {
            cancelled = true
        }
    }, [router])

    const statusCounts = applicationStatuses.reduce(
        (counts, status) => {
        counts[status] = applications.filter(
            (application) => application.status === status
        ).length

        return counts
        },
        {} as Record<ApplicationStatus, number>
    )

    const companies = [
        ...new Set(
            applications.map((application) => application.company)
        ),
    ].sort((first, second) =>
        first.localeCompare(second)
    )

    const roles = [
        ...new Set(
            applications.map((application) => application.role)
        ),
    ].sort((first, second) =>
        first.localeCompare(second)
    )

    const filteredApplications = applications.filter(
        (application) => {
            const matchesStatus =
                statusFilter === "all" ||
                application.status === statusFilter
            const matchesCompany =
                companyFilter === "all" ||
                application.company === companyFilter
            const matchesRole =
                roleFilter === "all" ||
                application.role === roleFilter
            const matchesAppliedDate =
                !appliedDateFilter ||
                application.applied_at === appliedDateFilter

            return (
                matchesStatus &&
                matchesCompany &&
                matchesRole &&
                matchesAppliedDate
            )
        }
    )

    if (loading) {
        return (
        <main className="min-h-screen bg-black pt-40 text-center">
            <div className="inline-block h-10 w-10 animate-spin rounded-full border-4 border-purple-500/20 border-t-purple-400" />
        </main>
        )
    }

    return (
        <main className="min-h-screen bg-black px-6 py-28 text-white">
        <div className="mx-auto max-w-6xl">
            <div className="mb-10 flex flex-wrap items-end justify-between gap-4">
            <div>
                <p className="text-sm text-purple-300">
                Application Tracker
                </p>

                <h1 className="mt-2 text-4xl font-bold">
                Applications
                </h1>

                <p className="mt-2 text-gray-400">
                Track real applications, follow-up dates, and
                document links in one workspace.
                </p>
            </div>

            <div className="flex flex-wrap gap-3">
                <Link
                    href="/applications/new"
                    className="rounded-xl bg-purple-600 px-4 py-2 font-semibold text-white hover:bg-purple-500"
                >
                    + Track application
                </Link>

                <Link
                    href="/history"
                    className="rounded-xl border border-purple-500/40 px-4 py-2 font-semibold text-purple-200 hover:bg-purple-500/10"
                >
                    Back to history
                </Link>
            </div>
            </div>

            {error && (
                <div className="mb-6 rounded-2xl border border-red-500/30 bg-red-500/10 px-5 py-4 text-red-200">
                    {error}
                </div>
            )}

            <section className="mb-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <article className="rounded-2xl border border-purple-500/20 bg-purple-500/10 p-5">
                    <p className="text-sm text-purple-200">
                    Total applications
                    </p>

                    <p className="mt-2 text-3xl font-bold">
                    {applications.length}
                    </p>
                </article>

                <article className="rounded-2xl border border-blue-500/20 bg-blue-500/10 p-5">
                    <p className="text-sm text-blue-200">Applied</p>

                    <p className="mt-2 text-3xl font-bold">
                    {statusCounts.applied}
                    </p>
                </article>

                <article className="rounded-2xl border border-yellow-500/20 bg-yellow-500/10 p-5">
                    <p className="text-sm text-yellow-200">
                    In process
                    </p>

                    <p className="mt-2 text-3xl font-bold">
                    {statusCounts.screening + statusCounts.interview}
                    </p>
                </article>

                <article className="rounded-2xl border border-green-500/20 bg-green-500/10 p-5">
                    <p className="text-sm text-green-200">Offers</p>

                    <p className="mt-2 text-3xl font-bold">
                    {statusCounts.offer}
                    </p>
                </article>
            </section>

            {applications.length === 0 ? (
            <section className="rounded-3xl border border-white/10 bg-white/5 px-6 py-16 text-center">
                <h2 className="text-2xl font-semibold">
                No applications tracked yet
                </h2>

                <p className="mx-auto mt-3 max-w-xl text-gray-400">
                Create an application to track its status, follow-up
                date, notes, and linked CareerPilot documents.
                </p>
            </section>
            ) : (
            <>
                <section>
                <div className="mb-5">
                    <h2 className="text-2xl font-semibold text-pink-200">
                    Recent activity
                    </h2>

                    <p className="mt-1 text-gray-400">
                    Most recently updated tracked applications.
                    </p>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                    {applications.slice(0, 6).map((application) => (
                    <Link
                        key={application.id}
                        href={`/applications/${application.id}`}
                        className="rounded-2xl border border-pink-500/20 bg-pink-500/10 p-5 transition hover:border-pink-500/50"
                    >
                        <p className="text-sm text-pink-300">
                        {formatStatus(application.status)}
                        </p>

                        <h3 className="mt-2 text-xl font-semibold">
                        {application.role}
                        </h3>

                        <p className="mt-1 text-gray-300">
                        {application.company}
                        </p>

                        <p className="mt-3 text-sm text-gray-500">
                        Updated{" "}
                        {new Date(
                            application.updated_at
                        ).toLocaleDateString()}
                        </p>
                    </Link>
                    ))}
                </div>
                </section>

                <section className="mt-10">
                <div className="mb-5">
                    <h2 className="text-2xl font-semibold text-purple-200">
                    All applications
                    </h2>

                    <p className="mt-1 text-gray-400">
                    Filter your saved applications by status, company, role,
                    or applied date.
                    </p>
                </div>

                <div className="grid gap-4 rounded-3xl border border-white/10 bg-white/5 p-5 md:grid-cols-4">
                    <label className="text-sm text-gray-300">
                    Status
                    <select
                        value={statusFilter}
                        onChange={(event) =>
                        setStatusFilter(
                            event.target.value as ApplicationStatus | "all"
                        )
                        }
                        className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-3 py-2 text-white"
                    >
                        <option value="all">All statuses</option>
                        {applicationStatuses.map((status) => (
                        <option key={status} value={status}>
                            {formatStatus(status)}
                        </option>
                        ))}
                    </select>
                    </label>

                    <label className="text-sm text-gray-300">
                    Company
                    <select
                        value={companyFilter}
                        onChange={(event) =>
                        setCompanyFilter(event.target.value)
                        }
                        className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-3 py-2 text-white"
                    >
                        <option value="all">All companies</option>
                        {companies.map((item) => (
                        <option key={item} value={item}>
                            {item}
                        </option>
                        ))}
                    </select>
                    </label>

                    <label className="text-sm text-gray-300">
                    Role
                    <select
                        value={roleFilter}
                        onChange={(event) =>
                        setRoleFilter(event.target.value)
                        }
                        className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-3 py-2 text-white"
                    >
                        <option value="all">All roles</option>
                        {roles.map((item) => (
                        <option key={item} value={item}>
                            {item}
                        </option>
                        ))}
                    </select>
                    </label>

                    <label className="text-sm text-gray-300">
                    Applied date
                    <input
                        type="date"
                        value={appliedDateFilter}
                        onChange={(event) =>
                        setAppliedDateFilter(event.target.value)
                        }
                        className="mt-2 w-full rounded-xl border border-purple-500/40 bg-black px-3 py-2 text-white"
                    />
                    </label>
                </div>

                {filteredApplications.length === 0 ? (
                    <div className="mt-5 rounded-2xl border border-white/10 bg-white/5 px-5 py-8 text-center text-gray-400">
                    No applications match the selected filters.
                    </div>
                ) : (
                    <div className="mt-5 overflow-x-auto rounded-3xl border border-white/10">
                    <table className="min-w-full text-left">
                        <thead className="bg-white/5 text-sm text-gray-400">
                        <tr>
                            <th className="px-5 py-4">Company</th>
                            <th className="px-5 py-4">Role</th>
                            <th className="px-5 py-4">Status</th>
                            <th className="px-5 py-4">Applied</th>
                            <th className="px-5 py-4">Next action</th>
                            <th className="px-5 py-4"> </th>
                        </tr>
                        </thead>

                        <tbody>
                        {filteredApplications.map((application) => (
                            <tr
                            key={application.id}
                            className="border-t border-white/10 text-gray-300"
                            >
                            <td className="px-5 py-4 font-medium">
                                {application.company}
                            </td>
                            <td className="px-5 py-4">
                                {application.role}
                            </td>
                            <td className="px-5 py-4">
                                {formatStatus(application.status)}
                            </td>
                            <td className="px-5 py-4">
                                {formatDate(application.applied_at)}
                            </td>
                            <td className="px-5 py-4">
                                {formatDate(application.next_action_date)}
                            </td>
                            <td className="px-5 py-4">
                                <Link
                                href={`/applications/${application.id}`}
                                className="font-semibold text-purple-300 hover:text-purple-200"
                                >
                                Open
                                </Link>
                            </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                    </div>
                )}
                </section>
            </>
            )}
        </div>
        </main>
    )
}
