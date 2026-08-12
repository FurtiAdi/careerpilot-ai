"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"

type User = {
    full_name: string
    email: string
    profile_picture_filename?: string
}

type Analysis = {
    id: number
    candidate_skills: string
    match_score: number
}

export default function ProfilePage() {

    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)
    const [stats, setStats] = useState({
        total_analyses: 0,
        average_match_score: 0,
        resume_uploaded: false
    })
    const [recentAnalyses, setRecentAnalyses] = useState<Analysis[]>([])
    const router = useRouter()

    useEffect(() => {

        const token = localStorage.getItem(
            "token"
        )

        if (!token) {
            router.push("/login")
            return
        }

        Promise.all([
            fetchProfile(),
            fetchProfileStats(),
            fetchRecentAnalyses()
        ]).finally(() => {
            setLoading(false)
        })

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

            if (response.status === 401) {

                localStorage.removeItem("token")

                router.push("/login")

                return
            }

            if (!response.ok) {
                throw new Error("Failed to fetch profile")
            }

            const data = await response.json()

            setUser(data)
        } catch (error) {
            console.error(error)
        }

    }

    const fetchProfileStats = async () => {

        try {

            const token = localStorage.getItem(
                "token"
            )

            const response = await fetch(
                "http://127.0.0.1:8000/profile-stats",
                {
                    headers: {
                    Authorization: `Bearer ${token}`
                    }
                }
            )

            const data = await response.json()

            setStats(data)

        } catch (error) {

            console.error(error)

        }

    }

    const fetchRecentAnalyses = async () => {

        try {

            const token = localStorage.getItem(
            "token"
            )

            const response = await fetch(
                "http://127.0.0.1:8000/analyses",
                {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                }
            )

            const data = await response.json()

            setRecentAnalyses(
                data.slice(0, 3)
            )

        } catch (error) {

            console.error(error)

        }

    }

    const uploadProfilePicture = async (
        file: File
        ) => {

        try {

            const token = localStorage.getItem(
                "token"
            )

            const formData = new FormData()

            formData.append("file", file)

            const response = await fetch(
                "http://127.0.0.1:8000/upload-profile-picture",
                {
                    method: "POST",
                    headers: {
                    Authorization: `Bearer ${token}`
                    },
                    body: formData
                }
            )

            const data = await response.json()

            setUser((prev: any) => ({
                ...prev,
                profile_picture_filename:
                    data.profile_picture_filename
            }))

        } catch (error) {

            console.error(error)

        }

    }

    if (loading) {

        return (

            <main className="min-h-screen bg-black flex items-center justify-center">

            <div
                className="
                w-12 h-12
                border-4
                border-purple-500/20
                border-t-purple-400
                rounded-full
                animate-spin
                "
            />

            </main>

        )
    }

    return (

        <main className="min-h-screen bg-black text-white pt-36 px-6 pb-20 overflow-hidden relative">

            {/* Glow Background */}
            <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-purple-600/10 blur-[160px] rounded-full" />

            <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-pink-600/10 blur-[160px] rounded-full" />

            <div className="relative z-10 max-w-5xl mx-auto grid lg:grid-cols-[320px_1fr] gap-8">

            {/* LEFT SIDEBAR */}
            <div
                className="
                h-fit sticky top-32
                rounded-3xl
                border border-white/10
                bg-white/5
                backdrop-blur-xl
                p-6
                "
            >

                {/* Avatar */}
                <div className="flex flex-col items-center text-center">

                    <label className="cursor-pointer">

                        <input
                            type="file"
                            accept="image/*"
                            className="hidden"
                            onChange={(e) => {

                                const file = e.target.files?.[0]

                                if (file) {

                                    uploadProfilePicture(file)

                                }

                            }}
                        />

                        <div
                            className="
                            w-32 h-32 rounded-full
                            bg-gradient-to-r
                            from-purple-500
                            to-pink-500
                            flex items-center justify-center
                            text-4xl font-bold
                            shadow-lg shadow-pink-500/20
                            overflow-hidden
                            "
                        >

                            {user?.profile_picture_filename ? (

                                <img
                                    src={`http://127.0.0.1:8000/uploads/profile_pictures/${user.profile_picture_filename}`}
                                    alt="Profile"
                                    className="
                                        w-full h-full
                                        object-cover
                                    "
                                />

                            ) : (

                                <span>

                                    {user?.full_name
                                    ?.split(" ")
                                    .map((name: string) =>
                                        name.charAt(0)
                                    )
                                    .join("")
                                    .slice(0, 2)}

                                </span>

                            )}

                        </div>

                    </label>

                    <h1 className="text-2xl font-bold mt-5">
                        {user?.full_name}
                    </h1>

                    <p className="text-gray-400 text-sm mt-2">
                        {user?.email}
                    </p>

                    <button
                        className="
                        mt-6 w-full
                        py-3 rounded-2xl
                        bg-white/5
                        border border-white/10
                        hover:border-purple-500/40
                        transition-all duration-300
                        "
                    >
                        Edit Profile
                    </button>

                </div>

                {/* Divider */}
                <div className="h-px bg-white/10 my-8" />

                {/* Stats */}
                <div className="space-y-5">

                <div className="flex items-center justify-between">

                    <span className="text-gray-400">
                    Analyses
                    </span>

                    <span className="font-semibold text-xl text-purple-300">
                    {stats.total_analyses}
                    </span>

                </div>

                <div className="flex items-center justify-between">

                    <span className="text-gray-400">
                    Avg Match
                    </span>

                    <span className="font-semibold text-xl text-pink-300">
                    {stats.average_match_score}%
                    </span>

                </div>

                <div className="flex items-center justify-between">

                    <span className="text-gray-400">
                    Resume
                    </span>

                    <span className="font-semibold text-green-400">
                    {stats.resume_uploaded ? "Uploaded" : "Not uploaded"}
                    </span>

                </div>

                </div>

            </div>

            {/* RIGHT CONTENT */}
            <div className="space-y-8">

                {/* Hero Card */}
                <div
                className="
                    rounded-3xl
                    border border-white/10
                    bg-gradient-to-br
                    from-purple-500/10
                    to-pink-500/10
                    backdrop-blur-xl
                    p-8
                "
                >

                <p className="text-purple-300 text-sm mb-3 uppercase tracking-widest">
                    CareerPilot AI
                </p>

                <h2 className="text-5xl font-bold leading-tight max-w-3xl">
                    Welcome back,
                    <br />
                    {user?.full_name}
                </h2>

                <p className="text-gray-400 mt-6 max-w-2xl leading-8">
                    Track your AI job analyses, optimize your resume,
                    and improve your interview performance using
                    intelligent career insights.
                </p>

                </div>

                {/* Dashboard Cards */}
                <div className="grid md:grid-cols-3 gap-6">

                <div
                    className="
                    rounded-3xl
                    border border-white/10
                    bg-white/5
                    p-6
                    hover:border-purple-500/30
                    transition-all duration-300
                    "
                >

                    <p className="text-gray-400 mb-4">
                    Resume Strength
                    </p>

                    <h3 className="text-4xl font-bold text-purple-300">
                    Strong
                    </h3>

                </div>

                <div
                    className="
                    rounded-3xl
                    border border-white/10
                    bg-white/5
                    p-6
                    hover:border-pink-500/30
                    transition-all duration-300
                    "
                >

                    <p className="text-gray-400 mb-4">
                    Interviews
                    </p>

                    <h3 className="text-4xl font-bold text-pink-300">
                    4
                    </h3>

                </div>

                <div
                    className="
                    rounded-3xl
                    border border-white/10
                    bg-white/5
                    p-6
                    hover:border-green-500/30
                    transition-all duration-300
                    "
                >

                    <p className="text-gray-400 mb-4">
                    Applications
                    </p>

                    <h3 className="text-4xl font-bold text-green-400">
                    18
                    </h3>

                </div>

                </div>

                {/* Activity Section */}
                <div
                className="
                    rounded-3xl
                    border border-white/10
                    bg-white/5
                    backdrop-blur-xl
                    p-8
                "
                >

                <div className="flex items-center justify-between mb-8">

                    <h2 className="text-2xl font-semibold">
                    Recent Activity
                    </h2>

                    <button
                    className="
                        px-5 py-2 rounded-xl
                        bg-white/5
                        border border-white/10
                        hover:border-purple-500/30
                    "
                    >
                    View All
                    </button>

                </div>

                <div className="space-y-5">

                    {recentAnalyses.map((analysis) => (

                        <div
                            key={analysis.id}
                            className="
                                flex items-center justify-between
                                p-5 rounded-2xl
                                bg-black/30
                                border border-white/5
                            "
                            >

                            <div>

                                <h3 className="font-semibold text-lg">
                                Analysis #{analysis.id}
                                </h3>

                                <p className="text-gray-400 text-sm mt-1">
                                    {analysis.candidate_skills?.slice(0, 80)}...
                                </p>

                            </div>

                            <div
                                className={`
                                    ${
                                    analysis.match_score >= 90
                                        ? "text-green-400"
                                        : "text-purple-300"
                                    }
                                    font-bold text-xl
                                `}
                                >
                                {analysis.match_score}%
                            </div>

                        </div>

                    ))}

                </div>

            </div>

        </div>

    </div>

        </main>
    )
}