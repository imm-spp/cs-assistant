import { useEffect, useState } from 'react'
import { fetchHealth } from './api'
import AskDocs from './AskDocs'
import CustomerList from './CustomerList'

type BackendStatus = 'loading' | 'ok' | 'error'
type Tab = 'customers' | 'docs'

function App() {
  const [status, setStatus] = useState<BackendStatus>('loading')
  const [tab, setTab] = useState<Tab>('customers')

  useEffect(() => {
    fetchHealth()
      .then((result) => setStatus(result === 'ok' ? 'ok' : 'error'))
      .catch(() => setStatus('error'))
  }, [])

  return (
    <main>
      <header>
        <h1>CS Assistant</h1>
        <p>ผู้ช่วย AI สำหรับทีมดูแลลูกค้า</p>
        <p className="status">
          สถานะ backend:{' '}
          {status === 'loading' && 'กำลังตรวจสอบ...'}
          {status === 'ok' && 'เชื่อมต่อแล้ว'}
          {status === 'error' && 'เชื่อมต่อไม่ได้'}
        </p>
      </header>

      <nav className="tabs" aria-label="เมนู">
        <button
          type="button"
          aria-pressed={tab === 'customers'}
          onClick={() => setTab('customers')}
        >
          ลูกค้า
        </button>
        <button type="button" aria-pressed={tab === 'docs'} onClick={() => setTab('docs')}>
          ถามจากเอกสาร
        </button>
      </nav>

      {tab === 'customers' && <CustomerList />}
      {tab === 'docs' && <AskDocs />}
    </main>
  )
}

export default App
