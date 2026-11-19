export interface HealthResponse {
  status: 'ok' | 'ready';
}
const baseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
export async function getHealth(signal?: AbortSignal): Promise<HealthResponse> {
  const response = await fetch(`${baseUrl}/health/live`, { signal });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  const data: unknown = await response.json();
  if (
    typeof data !== 'object' ||
    data === null ||
    !('status' in data) ||
    data.status !== 'ok'
  ) {
    throw new Error('Invalid health response');
  }
  return { status: data.status };
}
