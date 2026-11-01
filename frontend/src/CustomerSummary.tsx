import { useEffect, useState } from 'react'
import { summarizeCustomer, type Customer } from './api'

type Props = {
  customer: Customer
  onClose: () => void
}

// แสดงสรุปลูกค้าจาก AI ใช้ key={customer.id} ตอน render เพื่อเริ่มใหม่เมื่อเปลี่ยนลูกค้า
function CustomerSummary({ customer, onClose }: Props) {
  const [summary, setSummary] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    let ignore = false

    summarizeCustomer(customer.id)
      .then((text) => {
        if (!ignore) setSummary(text)
      })
      .catch(() => {
        if (!ignore) setError(true)
      })
      .finally(() => {
        if (!ignore) setLoading(false)
      })

    return () => {
      ignore = true
    }
  }, [customer.id])

  return (
    <aside className="summary" aria-label={`สรุปลูกค้า ${customer.name}`}>
      <div className="summary-header">
        <h3>สรุปลูกค้า: {customer.name}</h3>
        <button type="button" className="secondary" onClick={onClose}>
          ปิด
        </button>
      </div>
      {loading && <p>AI กำลังสรุป... (อาจใช้เวลาสักครู่)</p>}
      {!loading && error && <p role="alert">สรุปไม่สำเร็จ ลองใหม่อีกครั้ง</p>}
      {!loading && !error && <p className="summary-text">{summary}</p>}
    </aside>
  )
}

export default CustomerSummary
