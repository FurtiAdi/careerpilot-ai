const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {

  const isFormData = options.body instanceof FormData

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,

    headers: {
      ...(!isFormData && options.body
        ? {
            "Content-Type": "application/json",
          }
        : {}),
      ...options.headers,
    },
  })

  if (!response.ok) {
    let message = "Something went wrong"

    try {
      const error = await response.json()
      message = error.detail || error.error || message
    } catch {
      // Response was not JSON
    }

    throw new Error(message)
  }

  if (response.status === 204) {
    return undefined as T
  }

  const contentType = response.headers.get("content-type")

  if (
    contentType &&
    contentType.includes("application/json")
  ) {
    return response.json()
  }

  return undefined as T
}

export async function authenticatedApiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {

  const token = localStorage.getItem("token")

  if (!token) {
    throw new Error("Not authenticated")
  }

  return apiRequest<T>(endpoint, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: `Bearer ${token}`,
    },
  })
}