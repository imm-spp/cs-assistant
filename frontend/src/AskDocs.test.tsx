import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import AskDocs from './AskDocs'

const answer = {
  answer: 'ลิงก์ใช้ได้ 30 นาที (ที่มา: login-issues.md)',
  sources: [
    { source: 'login-issues.md', content: 'ลิงก์ใช้ได้ภายใน 30 นาที', score: 0.6829 },
    { source: 'support-sla.md', content: 'เวลาทำการ', score: 0.41 },
  ],
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('AskDocs', () => {
  it('ส่งคำถามแล้วแสดงคำตอบและเอกสารที่ใช้', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(answer)))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<AskDocs />)
    await user.type(screen.getByRole('textbox', { name: 'คำถาม' }), 'ลืมรหัสผ่าน')
    await user.click(screen.getByRole('button', { name: 'ถาม' }))

    expect(await screen.findByText(answer.answer)).toBeInTheDocument()
    expect(screen.getByText('login-issues.md')).toBeInTheDocument()
    expect(screen.getByText('ตรง 68%')).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/rag/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: 'ลืมรหัสผ่าน' }),
    })
  })

  it('กดคำถามตัวอย่างแล้วถามทันที', async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify(answer)))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<AskDocs />)
    await user.click(screen.getByRole('button', { name: 'ลูกค้าลืมรหัสผ่านต้องทำยังไง' }))

    expect(await screen.findByText(answer.answer)).toBeInTheDocument()
    expect(screen.getByRole('textbox', { name: 'คำถาม' })).toHaveValue('ลูกค้าลืมรหัสผ่านต้องทำยังไง')
  })

  it('แสดงข้อความ error เมื่อตอบไม่สำเร็จ', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 502 })))
    const user = userEvent.setup()

    render(<AskDocs />)
    await user.type(screen.getByRole('textbox', { name: 'คำถาม' }), 'hi')
    await user.click(screen.getByRole('button', { name: 'ถาม' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('ตอบไม่สำเร็จ')
  })

  it('สลับแท็บไปหน้าถามจากเอกสารได้', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string) =>
        Promise.resolve(new Response(JSON.stringify(url === '/api/health' ? { status: 'ok' } : []))),
      ),
    )
    const user = userEvent.setup()

    render(<App />)
    await user.click(screen.getByRole('button', { name: 'ถามจากเอกสาร' }))

    expect(screen.getByRole('heading', { name: 'ถามจากเอกสาร' })).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'รายชื่อลูกค้า' })).not.toBeInTheDocument()
  })
})
