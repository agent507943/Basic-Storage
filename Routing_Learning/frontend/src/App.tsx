import './App.css'

const tabs = ['Study', 'Quiz', 'Route Lab', 'OSPF Lab', 'History']

const metrics = [
  { label: 'Questions', value: '112' },
  { label: 'Difficulty', value: '3 levels' },
  { label: 'Review', value: 'Missed only' },
  { label: 'History', value: '20 attempts' },
]

const sampleQuestion = {
  question: 'In longest prefix match, which route is preferred?',
  choices: [
    'The route with the lowest administrative distance',
    'The route with the longest subnet mask',
    'The route learned first',
    'The static route',
  ],
  answer: 'The route with the longest subnet mask',
}

function App() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <div className="brand-mark">R</div>
          <div>
            <p className="eyebrow">CCNA / advanced prep</p>
            <h1>Routing Learning</h1>
          </div>
        </div>

        <nav className="nav" aria-label="Main navigation">
          {tabs.map((tab, index) => (
            <button
              key={tab}
              type="button"
              className={index === 1 ? 'nav-item active' : 'nav-item'}
            >
              {tab}
            </button>
          ))}
        </nav>

        <div className="status-card">
          <span className="status-dot" />
          <div>
            <strong>System status</strong>
            <p>Core learning engine ready</p>
          </div>
        </div>
      </aside>

      <main className="content-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow muted">Modernization preview</p>
            <h2>Exam-ready routing practice</h2>
          </div>
          <button type="button" className="primary-button">
            Start Quiz
          </button>
        </header>

        <section className="stats-grid" aria-label="Project metrics">
          {metrics.map((metric) => (
            <div key={metric.label} className="stat-card">
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </div>
          ))}
        </section>

        <section className="main-grid">
          <article className="quiz-card">
            <div className="card-header">
              <p className="eyebrow">Active question</p>
              <span className="tag">Medium</span>
            </div>

            <h3>{sampleQuestion.question}</h3>

            <div className="choices" role="list">
              {sampleQuestion.choices.map((choice) => (
                <button key={choice} type="button" className="choice-item">
                  {choice}
                </button>
              ))}
            </div>
          </article>

          <aside className="panel-card">
            <div className="card-header">
              <p className="eyebrow">Live summary</p>
              <span className="tag success">+10</span>
            </div>

            <div className="score-ring">
              <div className="score-inner">
                <strong>82%</strong>
                <span>score</span>
              </div>
            </div>

            <ul className="summary-list">
              <li>
                <span>Correct</span>
                <strong>9</strong>
              </li>
              <li>
                <span>Incorrect</span>
                <strong>2</strong>
              </li>
              <li>
                <span>Review queue</span>
                <strong>3</strong>
              </li>
            </ul>
          </aside>
        </section>

        <section className="lab-preview">
          <div className="lab-header">
            <div>
              <p className="eyebrow">Visualization preview</p>
              <h3>Longest Prefix Match</h3>
            </div>
            <span className="tag neutral">Route Lab</span>
          </div>

          <div className="topology">
            <div className="node edge">Edge</div>
            <div className="node router r1">R1</div>
            <div className="node router r2">R2</div>
            <div className="node router r3">R3</div>
            <div className="node lan lan-a">LAN-A</div>
            <div className="node lan lan-b">LAN-B</div>
            <div className="node lan lan-c">LAN-C</div>
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
