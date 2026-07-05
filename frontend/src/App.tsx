import { FormEvent, useState } from 'react'

type ResearchResponse = {
  topic: string
  sources: string[]
  report: string
  report_sections: {
    introduction: string
    key_findings: string[]
    conclusion: string
    sources_text: string
  }
  feedback: string
  feedback_sections: {
    score: number | null
    strengths: string[]
    areas_to_improve: string[]
    verdict: string
  }
  search_result: string
  reader_result: string
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000'

const defaultTopic = 'Artificial intelligence in healthcare'

export default function App() {
  const [topic, setTopic] = useState(defaultTopic)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState<ResearchResponse | null>(null)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(`${apiBaseUrl}/research`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic }),
      })

      if (!response.ok) {
        const errorBody = (await response.json().catch(() => null)) as { detail?: string } | null
        throw new Error(errorBody?.detail || `Request failed with status ${response.status}`)
      }

      const payload = (await response.json()) as ResearchResponse
      setData(payload)
    } catch (exception) {
      const message = exception instanceof Error ? exception.message : 'Something went wrong'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <main className="app-grid">
        <section className="hero-card">
          <div className="eyebrow">Multi-Agent Research Assistant</div>
          <h1>Search, read, write, and critique in one workflow.</h1>
          <p className="hero-copy">
            This assistant sends your topic through a search agent, reader agent, writer agent,
            and critic agent. The backend gathers live sources, synthesizes a report, and presents
            the result as a clean research dashboard.
          </p>

          <form className="topic-form" onSubmit={handleSubmit}>
            <label className="input-label" htmlFor="topic">
              Research topic
            </label>
            <div className="input-row">
              <input
                id="topic"
                value={topic}
                onChange={(event) => setTopic(event.target.value)}
                placeholder="Enter a topic to research"
              />
              <button type="submit" disabled={loading || !topic.trim()}>
                {loading ? 'Researching...' : 'Run research'}
              </button>
            </div>
          </form>

          {error ? <div className="error-banner">{error}</div> : null}

          <div className="stat-row">
            <div className="stat-pill">
              <span>Pipeline</span>
              <strong>{apiBaseUrl}</strong>
            </div>
            <div className="stat-pill">
              <span>Orchestrator</span>
              <strong>{loading ? 'Working' : data ? 'Ready' : 'Idle'}</strong>
            </div>
          </div>
        </section>

        <section className="content-grid">
          <article className="panel report-panel">
            <div className="panel-header">
              <div>
                <span className="panel-kicker">Writer Output</span>
                <h2>{data?.topic ?? 'Waiting for a topic'}</h2>
              </div>
              <div className="score-chip">
                {data?.feedback_sections.score ?? '—'}/10
              </div>
            </div>

            <div className="section-block">
              <h3>Introduction</h3>
              <p>{data?.report_sections.introduction || 'The report introduction will appear here after the writer agent runs.'}</p>
            </div>

            <div className="section-block">
              <h3>Key Findings</h3>
              <ul className="bullet-list">
                {(data?.report_sections.key_findings?.length ? data.report_sections.key_findings : ['Key findings will appear here after a run.']).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>

            <div className="section-block">
              <h3>Conclusion</h3>
              <p>{data?.report_sections.conclusion || 'The report conclusion will appear here after the writer agent runs.'}</p>
            </div>

            <details className="raw-details">
              <summary>Raw report text</summary>
              <pre>{data?.report || 'No report yet.'}</pre>
            </details>
          </article>

          <aside className="side-column">
            <article className="panel">
              <span className="panel-kicker">Critic Review</span>
              <h2>Feedback</h2>

              <div className="feedback-card">
                <span className="feedback-label">Strengths</span>
                <ul className="bullet-list compact">
                  {(data?.feedback_sections.strengths?.length ? data.feedback_sections.strengths : ['The critic feedback will appear here after a run.']).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="feedback-card">
                <span className="feedback-label">Areas to improve</span>
                <ul className="bullet-list compact">
                  {(data?.feedback_sections.areas_to_improve?.length ? data.feedback_sections.areas_to_improve : ['Areas to improve will appear here.']).map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>

              <div className="verdict-box">
                <span className="feedback-label">Verdict</span>
                <p>{data?.feedback_sections.verdict || 'The verdict will appear here.'}</p>
              </div>
            </article>

            <article className="panel">
              <span className="panel-kicker">Search Trail</span>
              <h2>Sources</h2>
              <div className="source-list">
                {(data?.sources?.length ? data.sources : ['Sources will appear here.']).map((source) => (
                  <a key={source} href={source.startsWith('http') ? source : '#'} target="_blank" rel="noreferrer">
                    {source}
                  </a>
                ))}
              </div>
            </article>

            <article className="panel">
              <details className="raw-details">
                <summary>Raw search and scrape output</summary>
                <div className="raw-stack">
                  <div>
                    <h3>Search result</h3>
                    <pre>{data?.search_result || 'No search result yet.'}</pre>
                  </div>
                  <div>
                    <h3>Reader result</h3>
                    <pre>{data?.reader_result || 'No reader result yet.'}</pre>
                  </div>
                </div>
              </details>
            </article>
          </aside>
        </section>
      </main>
    </div>
  )
}