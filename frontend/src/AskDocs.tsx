import { useState, type FormEvent } from 'react'
import { askDocs, type AskResult } from './api'

type Status = 'idle' | 'loading' | 'done' | 'error'

const EXAMPLE_QUESTIONS = [
  'ลูกค้าลืมรหัสผ่านต้องทำยังไง',
  'ค้างชำระ 20 วันจะเกิดอะไรขึ้น',
  'How fast does Premium support reply?',
]

function AskDocs() {
  const [question, setQuestion] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<AskResult | null>(null)

  async function ask(text: string) {
    if (!text.trim()) return
    setStatus('loading')
    try {
      setResult(await askDocs(text))
      setStatus('done')
    } catch {
      setStatus('error')
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    void ask(question)
  }

  function handleExample(text: string) {
    setQuestion(text)
    void ask(text)
  }

  return (
    <section>
      <h2>ถามจากเอกสาร</h2>
      <p className="hint">ตอบจากคู่มือใน docs/mock-kb เท่านั้น พร้อมบอกแหล่งที่มา</p>

      <form className="search" onSubmit={handleSubmit}>
        <input
          type="text"
          aria-label="คำถาม"
          placeholder="พิมพ์คำถาม เช่น ขอใบกำกับภาษีย้อนหลังได้กี่เดือน"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button type="submit" disabled={status === 'loading' || !question.trim()}>
          ถาม
        </button>
      </form>

      <div className="examples">
        ตัวอย่าง:
        {EXAMPLE_QUESTIONS.map((text) => (
          <button
            key={text}
            type="button"
            className="small"
            disabled={status === 'loading'}
            onClick={() => handleExample(text)}
          >
            {text}
          </button>
        ))}
      </div>

      {status === 'loading' && <p>AI กำลังค้นเอกสารและตอบ... (อาจใช้เวลาสักครู่)</p>}
      {status === 'error' && <p role="alert">ตอบไม่สำเร็จ ลองใหม่อีกครั้ง</p>}

      {status === 'done' && result && (
        <div className="answer">
          <h3>คำตอบ</h3>
          <p className="summary-text">{result.answer}</p>

          {result.sources.length > 0 && (
            <>
              <h3>เอกสารที่ใช้ตอบ</h3>
              <ul className="sources">
                {result.sources.map((source, index) => (
                  <li key={`${source.source}-${index}`}>
                    <details>
                      <summary>
                        {source.source}{' '}
                        <span className="score">ตรง {Math.round(source.score * 100)}%</span>
                      </summary>
                      <pre>{source.content}</pre>
                    </details>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </section>
  )
}

export default AskDocs
