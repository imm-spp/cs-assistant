import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { Customer } from './api'
import CustomerList from './CustomerList'

function makeCustomer(id: number, name: string, company: string, tier = 'standard'): Customer {
  return {
    id,
    name,
    company,
    tier,
    email: `customer${id}@example.com`,
    phone: '000-000-0000',
    notes: '',
    created_at: '2026-11-01T00:00:00Z',
  }
}

function jsonResponse(data: unknown): Response {
  return new Response(JSON.stringify(data))
}

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('CustomerList', () => {
  it('แสดงลูกค้าทั้งหมดในตาราง', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse([
          makeCustomer(1, 'Alice Mock', 'Globex', 'premium'),
          makeCustomer(2, 'สมชาย ทดสอบ', 'Acme'),
        ]),
      ),
    )

    render(<CustomerList />)

    const rows = await screen.findAllByRole('row')
    // แถวแรกคือหัวตาราง
    expect(rows).toHaveLength(3)
    expect(within(rows[1]).getByText('Alice Mock')).toBeInTheDocument()
    expect(within(rows[1]).getByText('Premium')).toBeInTheDocument()
    expect(within(rows[2]).getByText('customer2@example.com')).toBeInTheDocument()
    expect(screen.getByText('ทั้งหมด 2 ราย')).toBeInTheDocument()
    expect(fetch).toHaveBeenCalledWith('/api/customers')
  })

  it('ส่งคำค้นไปที่ API เมื่อกดค้นหา', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse([makeCustomer(1, 'Alice Mock', 'Globex')]))
      .mockResolvedValueOnce(jsonResponse([makeCustomer(2, 'Bob Mock', 'Acme')]))
    vi.stubGlobal('fetch', fetchMock)
    const user = userEvent.setup()

    render(<CustomerList />)
    await screen.findByText('Alice Mock')

    await user.type(screen.getByRole('searchbox', { name: 'ค้นหาลูกค้า' }), 'acme co')
    await user.click(screen.getByRole('button', { name: 'ค้นหา' }))

    expect(await screen.findByText('Bob Mock')).toBeInTheDocument()
    expect(screen.queryByText('Alice Mock')).not.toBeInTheDocument()
    expect(fetchMock).toHaveBeenLastCalledWith('/api/customers?q=acme%20co')
  })

  it('แสดงข้อความเมื่อไม่พบลูกค้า', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse([])))

    render(<CustomerList />)

    expect(await screen.findByText('ไม่พบลูกค้า')).toBeInTheDocument()
  })

  it('แสดงข้อความ error เมื่อโหลดไม่สำเร็จ', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('', { status: 500 })))

    render(<CustomerList />)

    expect(await screen.findByRole('alert')).toHaveTextContent('โหลดรายชื่อลูกค้าไม่สำเร็จ')
  })
})
