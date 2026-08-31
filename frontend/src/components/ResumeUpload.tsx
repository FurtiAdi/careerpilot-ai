interface ResumeUploadProps {
  resumeFile: File | null
  onUpload: (
    event: React.ChangeEvent<HTMLInputElement>
  ) => void
}

export default function ResumeUpload({
  resumeFile,
  onUpload,
}: ResumeUploadProps) {
  return (
    <div className="mb-8">
      <label
        className="
          flex items-center justify-center
          w-full h-24
          border border-white/10
          rounded-2xl
          bg-black/40
          hover:border-purple-400
          hover:bg-purple-500/5
          transition-all duration-300
          cursor-pointer
        "
      >
        <div className="text-center">
          <p className="text-lg font-medium text-white">
            Upload Resume
          </p>

          <p className="text-sm text-gray-500 mt-1">
            PDF files only
          </p>

          {resumeFile && (
            <p className="mt-2 text-purple-300 text-sm">
              {resumeFile.name}
            </p>
          )}
        </div>

        <input
          type="file"
          accept=".pdf"
          onChange={onUpload}
          className="hidden"
        />
      </label>
    </div>
  )
}