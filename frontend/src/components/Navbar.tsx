"use client"
import Link from "next/link"
import { Sparkles } from "lucide-react"
import { useRouter } from "next/navigation"


export default function Navbar() {
  const router = useRouter()

  const logoutUser = () => {

    localStorage.removeItem("token")

    router.push("/login")

  }


  return (

    <nav
      className="
        fixed top-0 left-0 w-full z-50
        backdrop-blur-xl
        bg-black/40
        border-b border-white/10
      "
    >

      <div
        className="
          max-w-6xl mx-auto
          px-6 py-4
          flex items-center justify-between
        "
      >

        {/* Logo Section */}
        <Link
            href="/"
            className="flex items-center gap-2"
        >

            {/* Logo Icon */}
            <div className="flex items-center justify-center">

                <Sparkles
                className="
                    w-6 h-6
                    text-white
                    stroke-[2.2]
                "
                />

            </div>

            {/* Brand Name */}
            <h1
                className="
                    text-2xl font-bold tracking-tight
                    bg-gradient-to-r
                    from-purple-200
                    via-purple-300
                    to-pink-400
                    text-transparent bg-clip-text
                "
            >
                CareerPilot AI
            </h1>

        </Link>

        {/* Navigation */}
        <div className="flex items-center gap-8">

          <Link
            href="/"
            className="
              text-gray-300
              hover:text-white
              transition
            "
          >
            Home
          </Link>

          <Link
            href="/history"
            className="
              text-gray-300
              hover:text-white
              transition
            "
          >
            History
          </Link>

          <button
            onClick={logoutUser}
            className="
              px-5 py-2 rounded-xl
              bg-red-500/10
              border border-red-500/20
              text-red-300
              hover:bg-red-500/20
              transition-all duration-300
            "
          >
            Logout
          </button>

        </div>

      </div>

    </nav>
  )
}