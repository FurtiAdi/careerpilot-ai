interface SkillMatchSectionProps {
  matchedRequired: string[]
  missingRequired: string[]
  matchedPreferred: string[]
  missingPreferred: string[]
}

export default function SkillMatchSection({
  matchedRequired,
  missingRequired,
  matchedPreferred,
  missingPreferred,
}: SkillMatchSectionProps) {
  return (
    <div className="grid md:grid-cols-2 gap-6 mb-8">
      {/* Required Skills */}
      <div className="bg-black/30 rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-6 text-green-400">
          ✅ Required Skills
        </h3>

        <div className="space-y-6">
          <div>
            <p className="text-sm text-gray-400 mb-3">
              Matched
            </p>

            <div className="flex flex-wrap gap-3">
              {matchedRequired.length > 0 ? (
                matchedRequired.map((skill) => (
                  <div
                    key={skill}
                    className="
                      px-4 py-2 rounded-full
                      bg-green-500/10
                      border border-green-500/20
                      text-green-300
                      text-sm font-medium
                    "
                  >
                    {skill}
                  </div>
                ))
              ) : (
                <p className="text-gray-500">
                  No required skills matched.
                </p>
              )}
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-400 mb-3">
              Missing
            </p>

            <div className="flex flex-wrap gap-3">
              {missingRequired.length > 0 ? (
                missingRequired.map((skill) => (
                  <div
                    key={skill}
                    className="
                      px-4 py-2 rounded-full
                      bg-red-500/10
                      border border-red-500/20
                      text-red-300
                      text-sm font-medium
                    "
                  >
                    {skill}
                  </div>
                ))
              ) : (
                <p className="text-gray-500">
                  No missing required skills.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Preferred Skills */}
      <div className="bg-black/30 rounded-2xl p-6">
        <h3 className="text-xl font-bold mb-6 text-blue-400">
          ⭐ Preferred Skills
        </h3>

        <div className="space-y-6">
          <div>
            <p className="text-sm text-gray-400 mb-3">
              Matched
            </p>

            <div className="flex flex-wrap gap-3">
              {matchedPreferred.length > 0 ? (
                matchedPreferred.map((skill) => (
                  <div
                    key={skill}
                    className="
                      px-4 py-2 rounded-full
                      bg-green-500/10
                      border border-green-500/20
                      text-green-300
                      text-sm font-medium
                    "
                  >
                    {skill}
                  </div>
                ))
              ) : (
                <p className="text-gray-500">
                  No preferred skills matched.
                </p>
              )}
            </div>
          </div>

          <div>
            <p className="text-sm text-gray-400 mb-3">
              Missing
            </p>

            <div className="flex flex-wrap gap-3">
              {missingPreferred.length > 0 ? (
                missingPreferred.map((skill) => (
                  <div
                    key={skill}
                    className="
                      px-4 py-2 rounded-full
                      bg-orange-500/10
                      border border-orange-500/20
                      text-orange-300
                      text-sm font-medium
                    "
                  >
                    {skill}
                  </div>
                ))
              ) : (
                <p className="text-gray-500">
                  No missing preferred skills.
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}