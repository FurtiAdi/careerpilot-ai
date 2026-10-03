import Link from "next/link"
import {
  BriefcaseBusiness,
  CalendarCheck2,
  CheckCircle2,
  Code2,
  FilePenLine,
  FileText,
  Heart,
  MapPin,
  MessageSquareText,
} from "lucide-react"

const demoJobs = [
  {
    title: "Backend Developer",
    company: "Tech Company AB",
    location: "Stockholm · Full-time",
    match: "92% match",
    icon: Code2,
    iconClassName: "bg-blue-500",
    matchClassName: "bg-emerald-100 text-emerald-700",
  },
  {
    title: "Administrator",
    company: "Kommunen",
    location: "Sigtuna · Full-time",
    match: "78% match",
    icon: FileText,
    iconClassName: "bg-amber-400",
    matchClassName: "bg-amber-100 text-amber-700",
  },
  {
    title: "Vårdbiträde",
    company: "Omsorgsbolaget",
    location: "Stockholm · Part-time",
    match: "71% match",
    icon: Heart,
    iconClassName: "bg-purple-600",
    matchClassName: "bg-amber-100 text-amber-700",
  },
]

const matchBreakdown = [
  ["Overall match", "92%", "w-full"],
  ["Skills match", "90%", "w-[90%]"],
  ["Experience match", "80%", "w-[80%]"],
  ["Education match", "100%", "w-full"],
  ["Role relevance", "90%", "w-[90%]"],
  ["Location & preferences", "95%", "w-[95%]"],
  ["Language match", "100%", "w-full"],
]

const featureCards = [
  {
    title: "Smart Job Matching",
    description:
      "Find opportunities that align with your skills, experience, and career goals.",
    icon: BriefcaseBusiness,
    iconClassName: "bg-purple-100 text-purple-600",
  },
  {
    title: "Tailored CV & Cover Letter",
    description:
      "Create focused application documents for each opportunity you pursue.",
    icon: FilePenLine,
    iconClassName: "bg-pink-100 text-pink-600",
  },
  {
    title: "Application Tracker",
    description:
      "Keep track of your applications, follow-ups, documents, and progress.",
    icon: CalendarCheck2,
    iconClassName: "bg-violet-100 text-violet-600",
  },
  {
    title: "Interview Preparation",
    description:
      "Prepare with personalized questions, guidance, and practical interview tips.",
    icon: MessageSquareText,
    iconClassName: "bg-rose-100 text-rose-600",
  },
]

const journeySteps = [
  {
    number: "01",
    title: "Upload your CV",
    description:
      "Share your experience so CareerPilot can understand your professional background.",
  },
  {
    number: "02",
    title: "Discover jobs",
    description:
      "Explore opportunities selected to match your skills and career direction.",
  },
  {
    number: "03",
    title: "Get insights",
    description:
      "See how each role aligns with your strengths and where you can improve.",
  },
  {
    number: "04",
    title: "Apply with confidence",
    description:
      "Prepare your application, track progress, and stay ready for next steps.",
  },
]

export default function Home() {
  return (
    <main className="min-h-screen overflow-hidden bg-slate-50 pt-24 text-slate-900">
      <section className="relative">
        <div className="absolute inset-x-0 top-0 h-[34rem] bg-gradient-to-br from-white via-purple-50 to-pink-50" />

        <div className="relative mx-auto grid max-w-7xl items-center gap-16 px-6 py-16 lg:grid-cols-[0.95fr_1.05fr] lg:py-24">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-purple-100 px-4 py-2 text-sm font-semibold text-purple-800">
              <SparklesIcon />
              AI-Powered Career Assistant
            </div>

            <h1 className="mt-8 max-w-2xl text-5xl font-bold leading-[1.04] tracking-tight text-slate-950 sm:text-6xl lg:text-7xl">
              Find the right jobs
              <br />
              for{" "}
              <span className="bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent">
                your future.
              </span>
            </h1>

            <p className="mt-7 max-w-xl text-xl leading-8 text-slate-500">
              CareerPilot helps you discover opportunities that match
              your skills, experience, and career goals—then prepares
              you to apply with confidence.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              <Link
                href="/register"
                className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 px-6 py-3.5 font-semibold text-white shadow-lg shadow-purple-500/20 transition hover:scale-[1.02] hover:opacity-90"
              >
                Get started →
              </Link>

              <a
                href="#how-it-works"
                className="rounded-xl border border-slate-200 bg-white px-6 py-3.5 font-semibold text-slate-900 shadow-sm transition hover:border-purple-300 hover:bg-purple-50"
              >
                See how it works
              </a>
            </div>

            <ul className="mt-9 flex flex-wrap gap-x-7 gap-y-3 text-sm text-slate-500">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-purple-600" />
                Find relevant jobs
              </li>

              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-purple-600" />
                Tailor your applications
              </li>

              <li className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-purple-600" />
                Track your progress
              </li>
            </ul>
          </div>

          <div className="relative mx-auto w-full max-w-2xl">
            <div className="absolute -inset-10 rounded-[4rem] bg-gradient-to-br from-purple-200/70 via-fuchsia-100 to-pink-200/70 blur-2xl" />

            <div className="relative rounded-3xl border border-slate-200 bg-white p-4 shadow-2xl shadow-purple-950/10">
              <div className="flex items-center gap-2 border-b border-slate-100 px-2 pb-4">
                <span className="h-2.5 w-2.5 rounded-full bg-purple-500" />
                <span className="h-2.5 w-2.5 rounded-full bg-blue-400" />
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
              </div>

              <div className="rounded-2xl bg-slate-50 p-5 sm:p-6">
                <div className="mb-5 flex items-center justify-between">
                  <h2 className="text-lg font-bold text-slate-900">
                    Recommended for you
                  </h2>

                  <span className="text-sm font-medium text-purple-700">
                    Demo preview
                  </span>
                </div>

                <div className="space-y-3">
                  {demoJobs.map((job) => {
                    const Icon = job.icon

                    return (
                      <article
                        key={job.title}
                        className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm sm:gap-4 sm:p-4"
                      >
                        <div
                          className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl text-white ${job.iconClassName}`}
                        >
                          <Icon className="h-5 w-5" />
                        </div>

                        <div className="min-w-0 flex-1">
                          <h3 className="truncate font-semibold text-slate-900">
                            {job.title}
                          </h3>

                          <p className="mt-1 truncate text-sm text-slate-500">
                            {job.company}
                          </p>

                          <p className="mt-1 flex items-center gap-1 text-xs text-slate-400">
                            <MapPin className="h-3.5 w-3.5" />
                            {job.location}
                          </p>
                        </div>

                        <span
                          className={`hidden rounded-lg px-2.5 py-1 text-xs font-semibold sm:inline-flex ${job.matchClassName}`}
                        >
                          {job.match}
                        </span>
                      </article>
                    )
                  })}
                </div>
              </div>
            </div>

            <aside className="relative mt-5 rounded-3xl border border-slate-200 bg-white p-5 shadow-xl shadow-slate-900/10 lg:absolute lg:-right-24 lg:bottom-3 lg:mt-0 lg:w-72">
              <h2 className="font-bold text-slate-900">
                Your match breakdown
              </h2>

              <div className="mt-5 space-y-3">
                {matchBreakdown.map(([label, score, width]) => (
                  <div key={label}>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-600">{label}</span>
                      <span className="font-semibold text-slate-800">
                        {score}
                      </span>
                    </div>

                    <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className={`h-full rounded-full bg-gradient-to-r from-emerald-400 to-emerald-500 ${width}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </aside>
          </div>
        </div>
      </section>

      <section
        id="features"
        className="border-y border-slate-200 bg-white"
      >
        <div className="mx-auto max-w-7xl px-6 py-16 lg:py-20">
          <div className="max-w-2xl">
            <p className="text-sm font-semibold text-purple-600">
              Everything in one place
            </p>

            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              A clearer way to manage your career journey.
            </h2>

            <p className="mt-4 text-lg leading-8 text-slate-500">
              CareerPilot brings matching, application preparation, and
              progress tracking together in one focused workspace.
            </p>
          </div>

          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {featureCards.map((feature) => {
              const Icon = feature.icon

              return (
                <article
                  key={feature.title}
                  className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:border-purple-200 hover:shadow-lg hover:shadow-purple-950/5"
                >
                  <div
                    className={`flex h-12 w-12 items-center justify-center rounded-2xl ${feature.iconClassName}`}
                  >
                    <Icon className="h-6 w-6" />
                  </div>

                  <h3 className="mt-5 text-lg font-bold text-slate-900">
                    {feature.title}
                  </h3>

                  <p className="mt-3 leading-7 text-slate-500">
                    {feature.description}
                  </p>
                </article>
              )
            })}
          </div>
        </div>
      </section>

      <section
        id="how-it-works"
        className="bg-slate-50"
      >
        <div className="mx-auto max-w-7xl px-6 py-16 lg:py-24">
          <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-start">
            <div>
              <p className="text-sm font-semibold text-purple-600">
                How it works
              </p>

              <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
                Your career journey in a few simple steps.
              </h2>

              <p className="mt-4 max-w-md text-lg leading-8 text-slate-500">
                CareerPilot is designed to help you move from your CV to
                a stronger application with clarity at every stage.
              </p>
            </div>

            <ol className="grid gap-6 sm:grid-cols-2">
              {journeySteps.map((step) => (
                <li
                  key={step.number}
                  className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
                >
                  <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-r from-purple-600 to-pink-500 text-sm font-bold text-white">
                    {step.number}
                  </span>

                  <h3 className="mt-5 text-lg font-bold text-slate-900">
                    {step.title}
                  </h3>

                  <p className="mt-3 leading-7 text-slate-500">
                    {step.description}
                  </p>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      <section
        id="about"
        className="border-t border-slate-200 bg-white"
      >
        <div className="mx-auto grid max-w-7xl gap-10 px-6 py-16 lg:grid-cols-[0.85fr_1.15fr] lg:items-center lg:py-24">
          <div>
            <p className="text-sm font-semibold text-purple-600">
              About CareerPilot
            </p>

            <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
              A more focused way to manage your job search.
            </h2>
          </div>

          <div className="rounded-3xl border border-purple-100 bg-gradient-to-br from-purple-50 to-pink-50 p-7 shadow-sm sm:p-9">
            <p className="text-lg leading-8 text-slate-600">
              CareerPilot is an AI-powered career assistant designed to make
              the job search more focused and manageable. It helps you
              discover relevant opportunities, understand how your background
              matches each role, prepare tailored applications, and keep track
              of your job search — all in one place.
            </p>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-200 bg-gradient-to-br from-purple-50 via-white to-pink-50">
        <div className="mx-auto max-w-4xl px-6 py-16 text-center lg:py-24">
          <p className="text-sm font-semibold text-purple-600">
            Build your next opportunity
          </p>

          <h2 className="mt-3 text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">
            Start building a more confident job search.
          </h2>

          <p className="mx-auto mt-5 max-w-2xl text-lg leading-8 text-slate-500">
            Create your CareerPilot account to prepare stronger
            applications, organize your progress, and get ready for
            what comes next.
          </p>

          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link
              href="/register"
              className="rounded-xl bg-gradient-to-r from-purple-600 to-pink-500 px-6 py-3.5 font-semibold text-white shadow-lg shadow-purple-500/20 transition hover:scale-[1.02] hover:opacity-90"
            >
              Get started →
            </Link>

            <Link
              href="/login"
              className="rounded-xl border border-slate-200 bg-white px-6 py-3.5 font-semibold text-slate-900 shadow-sm transition hover:border-purple-300 hover:bg-purple-50"
            >
              Log in
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-8 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <p>
            <span className="font-semibold text-slate-800">
              CareerPilot AI
            </span>{" "}
            — your career, with more clarity.
          </p>

          <div className="flex gap-5">
            <a
              href="#features"
              className="transition hover:text-purple-600"
            >
              Features
            </a>

            <a
              href="#how-it-works"
              className="transition hover:text-purple-600"
            >
              How it works
            </a>

            <Link
              href="/login"
              className="transition hover:text-purple-600"
            >
              Log in
            </Link>
          </div>
        </div>
      </footer>
    </main>
  )
}

function SparklesIcon() {
  return (
    <span
      aria-hidden="true"
      className="text-base leading-none text-purple-600"
    >
      ✦
    </span>
  )
}
