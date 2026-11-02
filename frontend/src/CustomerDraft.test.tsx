import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Customer } from './api'
import CustomerDraft from './CustomerDraft'
import CustomerList from './CustomerList'

const alice: Customer = {
  id: 7,
  name: 'Alice Mock',
  email: 'customer7@example.com',
  phone: '000-000-0000',
  company: 'Globex',
  tier: 'premium',
  notes: '',
  created_at: '2026-11-01T00:00:00Z',
}

function jsonResponse(data: unknown): Response {
  return new Response(JSON.stringify(data))
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('CustomerDraft', () => {
  it('ส่งคำสั่งและภาษาไปที่ API แล้วแสดงร่างข้อความ', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(jsonResponse({ customer_id: 7, language: 'en', draft: 'Dear Alice,' }))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<CustomerDraft customer={alice} onClose={() => {}} />)
    await user.type(screen.getByRole('textbox', { name: 'อยากสื่อสารเรื่องอะไร' }), 'follow up')
    await user.click(screen.getByRole('radio', { name: 'English' }))
    await user.click(screen.getByRole('button', { name: 'ร่างข้อความ' }))

    expect(await screen.findByDisplayValue('Dear Alice,')).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/ai/customers/7/draft', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ instruction: 'follow up', language: 'en' }),
    })
  })

  it('ปุ่มร่างข้อความกดไม่ได้ถ้ายังไม่พิมพ์คำสั่ง และเลือกภาษาไทยไว้ก่อน', () => {
    render(<CustomerDraft customer={alice} onClose={() => {}} />)

    expect(screen.getByRole('button', { name: 'ร่างข้อความ' })).toBeDisabled()
    expect(screen.getByRole('radio', { name: 'ไทย' })).toBeChecked()
  })

  it('คัดลอกร่างข้อความได้', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(jsonResponse({ customer_id: 7, language: 'th', draft: 'เรียน คุณ Alice' })),
    )
    const user = userEvent.setup()

    render(<CustomerDraft customer={alice} onClose={() => {}} />)
    await user.type(screen.getByRole('textbox', { name: 'อยากสื่อสารเรื่องอะไร' }), 'ทักทาย')
    await user.click(screen.getByRole('button', { name: 'ร่างข้อความ' }))
    await user.click(await screen.findByRole('button', { name: 'คัดลอก' }))

    expect(screen.getByRole('button', { name: 'คัดลอกแล้ว' })).toBeInTheDocument()
    expect(await navigator.clipboard.readText()).toBe('เรียน คุณ Alice')
  })

  it('แสดงข้อความ error เมื่อร่างไม่สำเร็จ', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 502 })))
    const user = userEvent.setup()

    render(<CustomerDraft customer={alice} onClose={() => {}} />)
    await user.type(screen.getByRole('textbox', { name: 'อยากสื่อสารเรื่องอะไร' }), 'hi')
    await user.click(screen.getByRole('button', { name: 'ร่างข้อความ' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('ร่างข้อความไม่สำเร็จ')
  })

  it('กดร่างข้อความในตารางแล้วเปิดฟอร์ม', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse([alice])))
    const user = userEvent.setup()

    render(<CustomerList />)
    await user.click(await screen.findByRole('button', { name: 'ร่างข้อความ Alice Mock' }))

    expect(screen.getByRole('heading', { name: 'ร่างข้อความถึง: Alice Mock' })).toBeInTheDocument()
  })
})
