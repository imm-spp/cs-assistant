import { useEffect, useState, type FormEvent } from 'react'
import { fetchCustomers, type Customer } from './api'

const TIER_LABELS: Record<string, string> = {
  standard: 'Standard',
  premium: 'Premium',
  enterprise: 'Enterprise',
}

function CustomerList() {
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [searchInput, setSearchInput] = useState('')
  // คำค้นที่ใช้จริง จะเปลี่ยนเมื่อกดปุ่มค้นหาเท่านั้น
  const [search, setSearch] = useState('')

  useEffect(() => {
    // กันไม่ให้ผลลัพธ์เก่าที่ตอบกลับมาช้ามาทับผลลัพธ์ใหม่
    let ignore = false

    fetchCustomers(search)
      .then((data) => {
        if (!ignore) setCustomers(data)
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
  }, [search])

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    // ถ้าคำค้นเหมือนเดิม effect จะไม่รันใหม่ จึงไม่ต้องแสดงสถานะกำลังโหลด
    if (searchInput === search) return
    setLoading(true)
    setError(false)
    setSearch(searchInput)
  }

  return (
    <section>
      <h2>รายชื่อลูกค้า</h2>

      <form className="search" role="search" onSubmit={handleSubmit}>
        <input
          type="search"
          aria-label="ค้นหาลูกค้า"
          placeholder="ค้นหาจากชื่อ อีเมล หรือบริษัท"
          value={searchInput}
          onChange={(event) => setSearchInput(event.target.value)}
        />
        <button type="submit">ค้นหา</button>
      </form>

      {loading && <p>กำลังโหลด...</p>}
      {!loading && error && <p role="alert">โหลดรายชื่อลูกค้าไม่สำเร็จ</p>}
      {!loading && !error && customers.length === 0 && <p>ไม่พบลูกค้า</p>}

      {!loading && !error && customers.length > 0 && (
        <>
          <p className="count">ทั้งหมด {customers.length} ราย</p>
          <table>
            <thead>
              <tr>
                <th>ชื่อ</th>
                <th>บริษัท</th>
                <th>อีเมล</th>
                <th>เบอร์โทร</th>
                <th>ระดับ</th>
              </tr>
            </thead>
            <tbody>
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td>{customer.name}</td>
                  <td>{customer.company}</td>
                  <td>{customer.email}</td>
                  <td>{customer.phone}</td>
                  <td>
                    <span className={`tier tier-${customer.tier}`}>
                      {TIER_LABELS[customer.tier] ?? customer.tier}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  )
}

export default CustomerList
