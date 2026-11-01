// รวมฟังก์ชันเรียก backend ไว้ที่เดียว (Vite proxy ส่ง /api ไปที่ localhost:8000)

export type Customer = {
  id: number
  name: string
  email: string
  phone: string
  company: string
  tier: string
  notes: string
  created_at: string
}

async function getJson<T>(url: string): Promise<T> {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }
  return response.json() as Promise<T>
}

export async function fetchHealth(): Promise<string> {
  const data = await getJson<{ status: string }>('/api/health')
  return data.status
}

// search ว่างหมายถึงดึงลูกค้าทั้งหมด
export async function fetchCustomers(search = ''): Promise<Customer[]> {
  const query = search.trim()
  const url = query ? `/api/customers?q=${encodeURIComponent(query)}` : '/api/customers'
  return getJson<Customer[]>(url)
}
