import { useEffect, useState } from 'react'
import { fetchHealth } from './api'
import CustomerList from './CustomerList'

type BackendStatus = 'loading' | 'ok' | 'error'

function App() {
  const [status, setStatus] = useState<BackendStatus>('loading')

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

      <CustomerList />
    </main>
  )
}

export default App
