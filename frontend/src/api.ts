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

async function getJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = init ? await fetch(url, init) : await fetch(url)
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

// ให้ AI สรุปลูกค้า (ใช้เวลาหลายวินาทีถ้าใช้ Ollama ในเครื่อง)
export async function summarizeCustomer(customerId: number): Promise<string> {
  const data = await getJson<{ summary: string }>(`/api/ai/customers/${customerId}/summary`, {
    method: 'POST',
  })
  return data.summary
}

export type DraftLanguage = 'th' | 'en'

// ให้ AI ร่างข้อความถึงลูกค้าตามคำสั่ง (instruction) เป็นภาษาไทยหรืออังกฤษ
export async function draftMessage(
  customerId: number,
  instruction: string,
  language: DraftLanguage,
): Promise<string> {
  const data = await getJson<{ draft: string }>(`/api/ai/customers/${customerId}/draft`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ instruction, language }),
  })
  return data.draft
}

export type AskSource = {
  source: string
  content: string
  score: number
}

export type AskResult = {
  answer: string
  sources: AskSource[]
}

// ถามคำถามจากเอกสารใน docs/mock-kb (RAG)
export async function askDocs(question: string): Promise<AskResult> {
  return getJson<AskResult>('/api/rag/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
}
