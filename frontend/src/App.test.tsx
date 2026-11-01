import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('App', () => {
  it('แสดงว่าเชื่อมต่อแล้ว เมื่อ backend ตอบ ok', async () => {
    // App เรียกทั้ง /api/health และ /api/customers จึงตอบตาม URL
    vi.stubGlobal(
      'fetch',
      vi.fn((url: string) =>
        Promise.resolve(
          new Response(JSON.stringify(url === '/api/health' ? { status: 'ok' } : [])),
        ),
      ),
    )

    render(<App />)

    expect(await screen.findByText(/เชื่อมต่อแล้ว/)).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'รายชื่อลูกค้า' })).toBeInTheDocument()
  })

  it('แสดงว่าเชื่อมต่อไม่ได้ เมื่อเรียก backend ไม่สำเร็จ', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('network')))

    render(<App />)

    expect(await screen.findByText(/เชื่อมต่อไม่ได้/)).toBeInTheDocument()
  })
})
