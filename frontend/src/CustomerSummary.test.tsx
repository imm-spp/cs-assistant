import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Customer } from './api'
import CustomerList from './CustomerList'
import CustomerSummary from './CustomerSummary'

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

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('CustomerSummary', () => {
  it('แสดงสรุปจาก AI', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ customer_id: 7, summary: '- ลูกค้า premium' })))
    vi.stubGlobal('fetch', fetchMock)

    render(<CustomerSummary customer={alice} onClose={() => {}} />)

    expect(screen.getByText(/AI กำลังสรุป/)).toBeInTheDocument()
    expect(await screen.findByText('- ลูกค้า premium')).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith('/api/ai/customers/7/summary', { method: 'POST' })
  })

  it('แสดงข้อความ error เมื่อสรุปไม่สำเร็จ', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 502 })))

    render(<CustomerSummary customer={alice} onClose={() => {}} />)

    expect(await screen.findByRole('alert')).toHaveTextContent('สรุปไม่สำเร็จ')
  })

  it('กดสรุปในตารางแล้วเปิดกล่องสรุป และกดปิดได้', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string) =>
        Promise.resolve(
          new Response(
            JSON.stringify(
              url === '/api/customers' ? [alice] : { customer_id: 7, summary: 'สรุปของ Alice' },
            ),
          ),
        ),
      ),
    )
    const user = userEvent.setup()

    render(<CustomerList />)
    await user.click(await screen.findByRole('button', { name: 'สรุป Alice Mock' }))

    expect(await screen.findByText('สรุปของ Alice')).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: 'ปิด' }))

    expect(screen.queryByText('สรุปของ Alice')).not.toBeInTheDocument()
  })
})
