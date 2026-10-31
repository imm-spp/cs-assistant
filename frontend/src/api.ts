// รวมฟังก์ชันเรียก backend ไว้ที่เดียว (Vite proxy ส่ง /api ไปที่ localhost:8000)

export async function fetchHealth(): Promise<string> {
  const response = await fetch('/api/health')
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  const data: { status: string } = await response.json()
  return data.status
}
