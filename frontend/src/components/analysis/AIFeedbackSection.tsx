import { AIAnalysis } from "@/services/analysisService"

interface AIFeedbackSectionProps {
  analysis: AIAnalysis
}

export default function AIFeedbackSection({
  analysis,
}: AIFeedbackSectionProps) {
  return (
    <div className="space-y-10">

      <div>
        <h4 className="text-2xl font-semibold mb-4 text-white">
          Summary
        </h4>

        <p className="max-w-4xl text-gray-300 leading-9 text-lg">
          {analysis.summary}
        </p>
      </div>

      <div>
        <h4 className="text-2xl font-semibold mb-4 text-green-400">
          Strengths
        </h4>

        <div className="grid gap-4">
          {analysis.strengths.map((item) => (
            <div
              key={item}
              className="bg-green-500/10 border border-green-500/20 rounded-2xl p-4 text-gray-200"
            >
              ✅ {item}
            </div>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-2xl font-semibold mb-4 text-red-400">
          Missing Requirements
        </h4>

        <div className="grid gap-4">
          {analysis.missing_requirements.map((item) => (
            <div
              key={item}
              className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 text-gray-200"
            >
              ❌ {item}
            </div>
          ))}
        </div>
      </div>

      <div>
        <h4 className="text-2xl font-semibold mb-4 text-purple-300">
          Recommendations
        </h4>

        <div className="grid gap-4">
          {analysis.recommendations.map((item) => (
            <div
              key={item}
              className="bg-purple-500/10 border border-purple-500/20 rounded-2xl p-4 text-gray-200"
            >
              💡 {item}
            </div>
          ))}
        </div>
      </div>

    </div>
  )
}