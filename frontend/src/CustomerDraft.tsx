import { useState, type FormEvent } from 'react'
import { draftMessage, type Customer, type DraftLanguage } from './api'

type Props = {
  customer: Customer
  onClose: () => void
}

type Status = 'idle' | 'loading' | 'done' | 'error'

// ฟอร์มให้ AI ร่างข้อความถึงลูกค้า ใช้ key={customer.id} ตอน render เพื่อเริ่มใหม่เมื่อเปลี่ยนลูกค้า
function CustomerDraft({ customer, onClose }: Props) {
  const [instruction, setInstruction] = useState('')
  const [language, setLanguage] = useState<DraftLanguage>('th')
  const [status, setStatus] = useState<Status>('idle')
  const [draft, setDraft] = useState('')
  const [copied, setCopied] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!instruction.trim()) return

    setStatus('loading')
    setCopied(false)
    try {
      setDraft(await draftMessage(customer.id, instruction, language))
      setStatus('done')
    } catch {
      setStatus('error')
    }
  }

  async function handleCopy() {
    await navigator.clipboard.writeText(draft)
    setCopied(true)
  }

  return (
    <aside className="summary" aria-label={`ร่างข้อความถึง ${customer.name}`}>
      <div className="summary-header">
        <h3>ร่างข้อความถึง: {customer.name}</h3>
        <button type="button" className="secondary" onClick={onClose}>
          ปิด
        </button>
      </div>

      <form className="draft-form" onSubmit={handleSubmit}>
        <label>
          อยากสื่อสารเรื่องอะไร
          <textarea
            rows={2}
            placeholder="เช่น ตามเรื่องค่าบริการค้างชำระอย่างสุภาพ"
            value={instruction}
            onChange={(event) => setInstruction(event.target.value)}
          />
        </label>

        <fieldset>
          <legend>ภาษา</legend>
          <label>
            <input
              type="radio"
              name="language"
              checked={language === 'th'}
              onChange={() => setLanguage('th')}
            />
            ไทย
          </label>
          <label>
            <input
              type="radio"
              name="language"
              checked={language === 'en'}
              onChange={() => setLanguage('en')}
            />
            English
          </label>
        </fieldset>

        <button type="submit" disabled={status === 'loading' || !instruction.trim()}>
          ร่างข้อความ
        </button>
      </form>

      {status === 'loading' && <p>AI กำลังร่างข้อความ... (อาจใช้เวลาสักครู่)</p>}
      {status === 'error' && <p role="alert">ร่างข้อความไม่สำเร็จ ลองใหม่อีกครั้ง</p>}
      {status === 'done' && (
        <div className="draft-result">
          <label>
            ร่างข้อความ (แก้ไขก่อนส่งได้)
            <textarea rows={8} value={draft} onChange={(event) => setDraft(event.target.value)} />
          </label>
          <button type="button" className="secondary" onClick={handleCopy}>
            {copied ? 'คัดลอกแล้ว' : 'คัดลอก'}
          </button>
        </div>
      )}
    </aside>
  )
}

export default CustomerDraft
