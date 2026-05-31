"use client"
import { useEffect, useState, useRef } from "react"
import Link from "next/link"
import { Sparkles } from "lucide-react"
import { useRouter } from "next/navigation"


export default function Navbar() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [openDropdown, setOpenDropdown] = useState(false)
  const router = useRouter()
  const dropdownRef = useRef<HTMLDivElement | null >(null)

  useEffect(() => {

    const handleClickOutside = (
      event: MouseEvent
    ) => {

      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(
          event.target as Node
        )
      ) {

        setOpenDropdown(false)

      }

    }

    document.addEventListener(
      "mousedown",
      handleClickOutside
    )

    return () => {

      document.removeEventListener(
        "mousedown",
        handleClickOutside
      )

    }

  }, [])

  
  useEffect(() => {

      const checkAuth = async () => {

          const token = localStorage.getItem(
              "token"
          )

          setIsAuthenticated(!!token)

          if (token) {

              await fetchUserProfile()

          }

      }

      checkAuth()

  }, [])

  const logoutUser = () => {
    localStorage.removeItem("token")
    setIsAuthenticated(false)
    setUser(null)
    setOpenDropdown(false)
    router.push("/login")
  }

  
  const fetchUserProfile = async () => {

    try {

      const token = localStorage.getItem(
        "token"
      )

      if (!token) return

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
        <div className="flex items-center gap-6">
          {isAuthenticated && (
            <>
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

          
              <div className="flex items-center gap-4">

                <Link
                  href="/history"
                  className="
                    px-5 py-2 rounded-xl
                    border border-white/10
                    hover:border-purple-500/40
                    transition-all duration-300
                  "
                >
                  History
                </Link>

                {/* User Dropdown */}
                <div ref={dropdownRef} className="relative">

                  <button
                    onClick={() =>
                      setOpenDropdown(!openDropdown)
                    }
                    className="
                      flex items-center gap-3
                      px-4 py-2 rounded-2xl
                      bg-white/5
                      border border-white/10
                      hover:border-purple-500/30
                      transition-all duration-300
                    "
                  >

                    {/* Avatar */}
                    <div
                      className="
                        w-10 h-10 rounded-full
                        bg-gradient-to-r
                        from-purple-500
                        to-pink-500
                        flex items-center justify-center
                        font-semibold
                      "
                    >
                      {user?.full_name?.charAt(0)}
                    </div>

                    {/* Name */}
                    <p className="text-sm text-white">
                      {user?.full_name
                        ?.split(" ")
                        .map((name: string) =>
                          name.charAt(0)
                        )
                        .join("")
                        .slice(0, 2)}
                    </p>

                  </button>

                  {/* Dropdown */}
                  {openDropdown && (

                    <div
                      className="
                        absolute right-0 mt-4
                        w-72
                        bg-black/95 
                        backdrop-blur-xl
                        animate-in fade-in zoom-in-95 duration-200
                        border border-white/10
                        rounded-3xl
                        p-5
                        shadow-2xl
                        z-50
                      "
                    >

                      {/* User Info */}
                      <div className="mb-4">

                        <p className="font-semibold text-lg">
                          {user?.full_name}
                        </p>

                        <p className="text-gray-400 text-sm mt-1">
                          {user?.email}
                        </p>

                      </div>

                      <div className="h-px bg-white/10 mb-4" />

                      {/* Profile */}
                      <button
                        onClick={() => {
                          setOpenDropdown(false)
                          router.push("/profile")
                        }}
                        className="
                          w-full text-left
                          px-4 py-3 rounded-2xl
                          hover:bg-white/5
                          transition-all duration-300
                        "
                      >
                        Profile
                      </button>

                      {/* Logout */}
                      <button
                        onClick={logoutUser}
                        className="
                          w-full text-left
                          px-4 py-3 rounded-2xl
                          text-red-300
                          hover:bg-red-500/10
                          transition-all duration-300
                        "
                      >
                        Logout
                      </button>

                    </div>

                  )}

                </div>

              </div>
              
            </>
          )}
                      
        </div>
      </div>
    </nav>
  )
}