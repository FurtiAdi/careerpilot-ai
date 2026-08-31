interface MatchScoreCardProps {
  score: number
}

export default function MatchScoreCard({
  score,
}: MatchScoreCardProps) {
  return (
    <div className="bg-black/30 rounded-2xl p-6">
      <h3 className="text-2xl font-bold mb-6 flex items-center gap-3">
        📊 Match Score
      </h3>

      <div className="flex flex-col items-center justify-center">
        <div className="relative w-52 h-52">
          <svg
            className="w-full h-full rotate-[-90deg]"
            viewBox="0 0 200 200"
          >
            <circle
              cx="100"
              cy="100"
              r="85"
              stroke="rgba(255,255,255,0.08)"
              strokeWidth="14"
              fill="none"
            />

            <circle
              cx="100"
              cy="100"
              r="85"
              stroke="url(#matchScoreGradient)"
              strokeWidth="14"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={534}
              strokeDashoffset={
                534 - (534 * score) / 100
              }
              className="
                transition-all
                duration-[2000ms]
                ease-out
              "
            />

            <defs>
              <linearGradient
                id="matchScoreGradient"
                x1="0%"
                y1="0%"
                x2="100%"
                y2="100%"
              >
                <stop
                  offset="0%"
                  stopColor="#a855f7"
                />

                <stop
                  offset="100%"
                  stopColor="#ec4899"
                />
              </linearGradient>
            </defs>
          </svg>

          <div
            className="
              absolute inset-0
              flex flex-col
              items-center justify-center
            "
          >
            <p className="text-gray-400 text-sm mb-2">
              Match Score
            </p>

            <h2
              className="
                text-5xl font-bold
                bg-gradient-to-r
                from-purple-300
                to-pink-400
                text-transparent bg-clip-text
              "
            >
              {score}%
            </h2>
          </div>
        </div>
      </div>
    </div>
  )
}