import { useEffect, useMemo, useState } from 'react'
import './App.css'
import questionsData from '../../questions.json'

type Question = {
  difficulty: 'easy' | 'medium' | 'hard'
  question: string
  choices: string[]
  answer: string
  explanation: string
  hint: string
}

type HistoryEntry = {
  score: number
  percentage: number
  difficulty: string
  date: string
}

type TabKey = 'Study' | 'Quiz' | 'Route Lab' | 'OSPF Lab' | 'History'

type RouteEntry = {
  prefix: string
  protocol: string
  ad: number
  metric: number
  next_hop: string
  interface: string
  path: string[]
  color: string
}

type RouteScenarioKey = 'LPM default test' | 'BGP exit test' | 'Summary route test'

type OSPFScenarioKey = 'Backbone and ABR' | 'Stub area' | 'DR election'

type OSPFLsaRow = {
  lsa: string
  area: string
  source: string
  meaning: string
}

const tabs: TabKey[] = ['Study', 'Quiz', 'Route Lab', 'OSPF Lab', 'History']
const difficultyOptions = ['easy', 'medium', 'hard'] as const
const questionCounts = [10, 15, 20, 25]
const focusPills = ['Longest prefix match', 'AD + metric', 'OSPF areas', 'DR / BDR']

const studyOverview = [
  {
    title: 'Longest prefix match',
    text: 'The most specific route wins first. A /25 beats a /24, and both beat a default route unless the topology forces a different policy.',
  },
  {
    title: 'Administrative distance',
    text: 'When prefix lengths tie, AD decides the preferred route. Static routes outrank OSPF, OSPF outranks EIGRP, and BGP is generally used for internet exit paths.',
  },
  {
    title: 'OSPF areas',
    text: 'Area 0 is the backbone. ABRs summarize routes between areas, while stub areas block external Type 5 LSAs and rely on a default route.',
  },
  {
    title: 'DR and BDR',
    text: 'On shared Ethernet segments, the highest OSPF priority becomes the DR and the next highest becomes the BDR. DROTHER routers only exchange with the DR/BDR.',
  },
]

const routeNodes = [
  { id: 'Edge', x: 72, y: 110 },
  { id: 'R1', x: 210, y: 52 },
  { id: 'R2', x: 210, y: 120 },
  { id: 'R3', x: 210, y: 188 },
  { id: 'LAN-A', x: 392, y: 52 },
  { id: 'LAN-B', x: 392, y: 120 },
  { id: 'LAN-C', x: 392, y: 188 },
  { id: 'ISP', x: 520, y: 70 },
  { id: 'Backup ISP', x: 520, y: 170 },
  { id: 'Internet', x: 610, y: 120 },
] as const

const routeNodeMap = Object.fromEntries(routeNodes.map((node) => [node.id, node])) as Record<string, (typeof routeNodes)[number]>

const routeLabRoutes: RouteEntry[] = [
  {
    prefix: '10.10.1.128/25',
    protocol: 'Static',
    ad: 1,
    metric: 0,
    next_hop: 'R1',
    interface: 'Gi0/0',
    path: ['Edge', 'R1', 'LAN-A'],
    color: '#ff7043',
  },
  {
    prefix: '10.10.1.0/24',
    protocol: 'OSPF',
    ad: 110,
    metric: 20,
    next_hop: 'R2',
    interface: 'Gi0/1',
    path: ['Edge', 'R2', 'LAN-B'],
    color: '#42a5f5',
  },
  {
    prefix: '10.10.0.0/16',
    protocol: 'EIGRP',
    ad: 90,
    metric: 30720,
    next_hop: 'R3',
    interface: 'Gi0/2',
    path: ['Edge', 'R3', 'LAN-C'],
    color: '#66bb6a',
  },
  {
    prefix: '10.0.0.0/8',
    protocol: 'BGP',
    ad: 20,
    metric: 100,
    next_hop: 'ISP',
    interface: 'Gi0/3',
    path: ['Edge', 'ISP', 'Internet'],
    color: '#ab47bc',
  },
  {
    prefix: '0.0.0.0/0',
    protocol: 'BGP Default',
    ad: 200,
    metric: 200,
    next_hop: 'Backup ISP',
    interface: 'Gi0/4',
    path: ['Edge', 'Backup ISP', 'Internet'],
    color: '#8d6e63',
  },
]

const routeLabScenarios: Record<RouteScenarioKey, { destination: string; focus: string[] }> = {
  'LPM default test': {
    destination: '10.10.1.130',
    focus: ['10.10.1.128/25', '10.10.1.0/24', '10.10.0.0/16', '10.0.0.0/8', '0.0.0.0/0'],
  },
  'BGP exit test': {
    destination: '10.44.5.9',
    focus: ['10.0.0.0/8', '0.0.0.0/0'],
  },
  'Summary route test': {
    destination: '10.10.3.14',
    focus: ['10.10.0.0/16', '10.0.0.0/8', '0.0.0.0/0'],
  },
}

const ospfLabScenarios: Record<
  OSPFScenarioKey,
  {
    summary: string
    highlight: string[]
    roles: Record<string, string>
    lsa_rows: OSPFLsaRow[]
  }
> = {
  'Backbone and ABR': {
    summary: 'R2 is the ABR between Area 0 and Area 1. Type 3 summaries cross the boundary; Type 1 stays local.',
    highlight: ['R1', 'R2 ABR', 'R4', 'R5', 'LAN0', 'LAN1'],
    roles: {
      R1: 'Internal router',
      'R2 ABR': 'ABR',
      R3: 'Internal router',
      R4: 'Internal router',
      R5: 'Internal router',
    },
    lsa_rows: [
      { lsa: 'Type 1', area: 'Area 0', source: 'R1 / R2', meaning: 'Router links stay within the local area.' },
      { lsa: 'Type 2', area: 'Area 0', source: 'LAN0 DR', meaning: 'Multi-access network information is advertised in the area.' },
      { lsa: 'Type 3', area: 'Area 1', source: 'R2 ABR', meaning: 'Summary routes are injected into the other area.' },
      { lsa: 'Type 5', area: 'External', source: 'ASBR', meaning: 'External routes are filtered out in a stub-style design.' },
    ],
  },
  'Stub area': {
    summary: 'A stub area blocks Type 5 external LSAs and uses a default route toward the ABR instead.',
    highlight: ['R2 ABR', 'R4', 'R5', 'LAN1'],
    roles: {
      'R2 ABR': 'ABR / default route source',
      R4: 'Stub area internal router',
      R5: 'Stub area internal router',
    },
    lsa_rows: [
      { lsa: 'Type 1', area: 'Area 1', source: 'R4 / R5', meaning: 'Stub routers still exchange local topology.' },
      { lsa: 'Type 3', area: 'Area 1', source: 'R2 ABR', meaning: 'Summary routes remain allowed inside the stub area.' },
      { lsa: 'Type 5', area: 'Area 1', source: 'Blocked', meaning: 'External LSAs are filtered out in a true stub area.' },
      { lsa: 'Default', area: 'Area 1', source: 'R2 ABR', meaning: 'The default route is used instead of external details.' },
    ],
  },
  'DR election': {
    summary: 'On a broadcast segment, the router with the highest OSPF priority becomes DR; the next highest becomes BDR.',
    highlight: ['R1', 'R2 ABR', 'R3', 'LAN0'],
    roles: {
      R1: 'Priority 1 - DROTHER',
      'R2 ABR': 'Priority 100 - DR',
      R3: 'Priority 50 - BDR',
    },
    lsa_rows: [
      { lsa: 'DR', area: 'Area 0', source: 'R2 ABR', meaning: 'Highest priority wins the DR election on the shared LAN.' },
      { lsa: 'BDR', area: 'Area 0', source: 'R3', meaning: 'The next-highest priority router becomes the backup.' },
      { lsa: 'DROTHER', area: 'Area 0', source: 'R1', meaning: 'Other routers do not participate as DR/BDR.' },
      { lsa: 'Type 2', area: 'Area 0', source: 'LAN0 DR', meaning: 'The DR originates the network LSA for the segment.' },
    ],
  },
}

const buildQuestionKey = (question: Question) => `${question.difficulty}::${question.question}`

const shuffle = <T,>(items: T[]) => {
  const copy = [...items]
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}

const ipv4ToInt = (value: string) => {
  const parts = value.trim().split('.')
  if (parts.length !== 4) return null

  const numbers = parts.map((part) => Number(part))
  if (numbers.some((number) => !Number.isInteger(number) || number < 0 || number > 255)) return null

  return ((numbers[0] << 24) | (numbers[1] << 16) | (numbers[2] << 8) | numbers[3]) >>> 0
}

const ipInPrefix = (address: number, prefix: string) => {
  const [networkText, prefixLengthText] = prefix.split('/')
  const prefixLength = Number(prefixLengthText)
  if (!Number.isInteger(prefixLength) || prefixLength < 0 || prefixLength > 32) return false

  const networkAddress = ipv4ToInt(networkText)
  if (networkAddress === null) return false

  const mask = prefixLength === 0 ? 0 : ((0xffffffff << (32 - prefixLength)) >>> 0)
  return (address & mask) >>> 0 === (networkAddress & mask) >>> 0
}

function App() {
  const [activeTab, setActiveTab] = useState<TabKey>('Quiz')
  const [difficulty, setDifficulty] = useState<(typeof difficultyOptions)[number]>('easy')
  const [questionCount, setQuestionCount] = useState<number>(10)
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [score, setScore] = useState(0)
  const [correctCount, setCorrectCount] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null)
  const [showHint, setShowHint] = useState(false)
  const [showExplanation, setShowExplanation] = useState(false)
  const [statusMessage, setStatusMessage] = useState('Ready for a new routing round.')
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [reviewQueue, setReviewQueue] = useState<string[]>([])
  const [routeScenario, setRouteScenario] = useState<RouteScenarioKey>('LPM default test')
  const [routeDestination, setRouteDestination] = useState(routeLabScenarios['LPM default test'].destination)
  const [routeMatches, setRouteMatches] = useState<RouteEntry[]>([])
  const [routeWinner, setRouteWinner] = useState<RouteEntry | null>(null)
  const [routeSummary, setRouteSummary] = useState('Choose a scenario and click Analyze Route.')
  const [routeDetail, setRouteDetail] = useState('Longest-prefix-match rules are applied before AD and metric evaluation.')
  const [ospfScenario, setOspfScenario] = useState<OSPFScenarioKey>('Backbone and ABR')

  const currentQuestion = questions[currentIndex]

  useEffect(() => {
    try {
      const storedHistory = localStorage.getItem('routing-learning-history')
      const storedReview = localStorage.getItem('routing-learning-review')
      if (storedHistory) setHistory(JSON.parse(storedHistory))
      if (storedReview) setReviewQueue(JSON.parse(storedReview))
    } catch {
      // ignore local storage errors
    }
  }, [])

  useEffect(() => {
    localStorage.setItem('routing-learning-history', JSON.stringify(history))
  }, [history])

  useEffect(() => {
    localStorage.setItem('routing-learning-review', JSON.stringify(reviewQueue))
  }, [reviewQueue])

  const totalQuestions = questions.length
  const currentProgress = totalQuestions ? Math.round(((currentIndex + 1) / totalQuestions) * 100) : 0

  const metrics = useMemo(
    () => [
      { label: 'Questions', value: String((questionsData as Question[]).length) },
      { label: 'Difficulty', value: `${difficultyOptions.length} levels` },
      { label: 'Review', value: String(reviewQueue.length) },
      { label: 'History', value: `${history.length} attempts` },
    ],
    [history.length, reviewQueue.length],
  )

  const analyzeRouteLab = () => {
    const addressValue = ipv4ToInt(routeDestination)
    if (addressValue === null) {
      setRouteMatches([])
      setRouteWinner(null)
      setRouteSummary('Invalid destination IP address.')
      setRouteDetail('Enter a valid IPv4 address to calculate the winning route.')
      return
    }

    const matches = routeLabRoutes
      .filter((route) => ipInPrefix(addressValue, route.prefix))
      .sort((left, right) => {
        const leftLength = Number(left.prefix.split('/')[1])
        const rightLength = Number(right.prefix.split('/')[1])
        return rightLength - leftLength || left.ad - right.ad || left.metric - right.metric
      })

    if (!matches.length) {
      setRouteMatches([])
      setRouteWinner(null)
      setRouteSummary('No matching route found for this destination.')
      setRouteDetail('Without a more specific route or default route, the packet would be dropped.')
      return
    }

    const winner = matches[0]
    setRouteMatches(matches)
    setRouteWinner(winner)
    setRouteSummary(`Best match: ${winner.prefix} via ${winner.protocol} from ${winner.next_hop}.`)
    setRouteDetail(
      `Reason: longest prefix match wins first, then the router compares administrative distance and metric for equal-length prefixes.`,
    )
  }

  const loadRouteScenario = (scenario: RouteScenarioKey) => {
    setRouteScenario(scenario)
    setRouteDestination(routeLabScenarios[scenario].destination)
    setTimeout(() => analyzeRouteLab(), 0)
  }

  const startQuiz = () => {
    const pool = (questionsData as Question[]).filter((question) => question.difficulty === difficulty)
    const selected = shuffle(pool).slice(0, Math.min(questionCount, pool.length))

    if (!selected.length) {
      setStatusMessage(`No ${difficulty} questions are available yet.`)
      return
    }

    setQuestions(selected)
    setCurrentIndex(0)
    setScore(0)
    setCorrectCount(0)
    setSelectedAnswer(null)
    setShowHint(false)
    setShowExplanation(false)
    setStatusMessage(`Quiz started: ${selected.length} ${difficulty} questions.`)
    setActiveTab('Quiz')
  }

  const handleAnswer = (choice: string) => {
    if (!currentQuestion || selectedAnswer) return

    setSelectedAnswer(choice)
    setShowExplanation(true)

    if (choice === currentQuestion.answer) {
      setScore((previous) => previous + 10)
      setCorrectCount((previous) => previous + 1)
      setStatusMessage('Correct! +10 points.')
      return
    }

    setScore((previous) => previous - 5)
    setReviewQueue((previous) => [...new Set([...previous, buildQuestionKey(currentQuestion)])])
    setStatusMessage(`Incorrect. Correct answer: ${currentQuestion.answer}`)
  }

  const finishQuiz = () => {
    const percentage = totalQuestions ? Math.round((correctCount / totalQuestions) * 100) : 0
    const entry: HistoryEntry = {
      score,
      percentage,
      difficulty,
      date: new Date().toISOString(),
    }

    setHistory((previous) => [entry, ...previous].slice(0, 20))
    setQuestions([])
    setCurrentIndex(0)
    setSelectedAnswer(null)
    setShowHint(false)
    setShowExplanation(false)
    setStatusMessage(`Finished with ${percentage}% in ${difficulty}.`)
    setActiveTab('History')
  }

  const nextQuestion = () => {
    if (!questions.length) return

    if (currentIndex >= questions.length - 1) {
      finishQuiz()
      return
    }

    setCurrentIndex((index) => index + 1)
    setSelectedAnswer(null)
    setShowHint(false)
    setShowExplanation(false)
    setStatusMessage(`Question ${currentIndex + 2} of ${questions.length}.`)
  }

  const startReview = () => {
    const reviewQuestions = shuffle(
      (questionsData as Question[]).filter((question) => reviewQueue.includes(buildQuestionKey(question))),
    )

    if (!reviewQuestions.length) {
      setStatusMessage('The review queue is empty. Missed questions will appear here.')
      return
    }

    setQuestions(reviewQuestions)
    setCurrentIndex(0)
    setScore(0)
    setCorrectCount(0)
    setSelectedAnswer(null)
    setShowHint(false)
    setShowExplanation(false)
    setStatusMessage(`Review mode: ${reviewQuestions.length} missed questions.`)
    setActiveTab('Quiz')
  }

  const clearReview = () => {
    setReviewQueue([])
    setStatusMessage('Review queue cleared.')
  }

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
          {tabs.map((tab) => (
            <button
              key={tab}
              type="button"
              className={activeTab === tab ? 'nav-item active' : 'nav-item'}
              onClick={() => setActiveTab(tab)}
            >
              {tab}
            </button>
          ))}
        </nav>

        <div className="status-card">
          <span className="status-dot" />
          <div>
            <strong>System status</strong>
            <p>{statusMessage}</p>
          </div>
        </div>
      </aside>

      <main className="content-panel">
        <header className="topbar">
          <div>
            <p className="eyebrow muted">Modernization preview</p>
            <h2>Exam-ready routing practice</h2>
            <div className="header-badges" aria-label="Core routing concepts">
              {focusPills.map((pill) => (
                <span key={pill} className="pill">
                  {pill}
                </span>
              ))}
            </div>
          </div>
          <button type="button" className="primary-button" onClick={startQuiz}>
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

        {activeTab === 'Study' && (
          <section className="study-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Curriculum</p>
                <h3>Study guide</h3>
              </div>
            </div>
            <div className="study-grid">
              {studyOverview.map((topic) => (
                <article key={topic.title} className="glass-card">
                  <h4>{topic.title}</h4>
                  <p className="study-copy">{topic.text}</p>
                </article>
              ))}
            </div>

            <div className="study-readout">
              <h4>Advanced topics to continue practicing</h4>
              <ul>
                <li>BGP path selection and default route use</li>
                <li>VRF segmentation and route leaks</li>
                <li>MPLS forwarding concepts and traffic engineering</li>
                <li>IPv6, multicast, and RPF checks</li>
              </ul>
            </div>
          </section>
        )}

        {activeTab === 'Quiz' && (
          <section className="main-grid">
            <article className="quiz-card">
              <div className="card-header">
                <p className="eyebrow">Active question</p>
                <span className="tag">{currentQuestion?.difficulty ?? 'Ready'}</span>
              </div>

              {currentQuestion ? (
                <>
                  <div className="question-meta">
                    <strong>
                      {currentIndex + 1}/{questions.length}
                    </strong>
                    <span>{currentProgress}% complete</span>
                  </div>
                  <h3>{currentQuestion.question}</h3>

                  <div className="choices" role="list">
                    {currentQuestion.choices.map((choice) => {
                      const isSelected = selectedAnswer === choice
                      const isCorrect = currentQuestion.answer === choice
                      const revealChoice = selectedAnswer !== null && (isSelected || isCorrect)

                      return (
                        <button
                          key={choice}
                          type="button"
                          className={[
                            'choice-item',
                            revealChoice && isCorrect ? 'correct' : '',
                            revealChoice && isSelected && !isCorrect ? 'incorrect' : '',
                          ]
                            .filter(Boolean)
                            .join(' ')}
                          onClick={() => handleAnswer(choice)}
                          disabled={selectedAnswer !== null}
                        >
                          {choice}
                        </button>
                      )
                    })}
                  </div>

                  {showHint && (
                    <div className="hint-box">
                      <strong>Hint:</strong> {currentQuestion.hint}
                    </div>
                  )}

                  {showExplanation && (
                    <div className="explanation-box">
                      <strong>Explanation:</strong> {currentQuestion.explanation}
                    </div>
                  )}

                  <div className="quiz-actions">
                    <button type="button" className="secondary-button" onClick={() => setShowHint((value) => !value)}>
                      {showHint ? 'Hide hint' : 'Show hint'}
                    </button>
                    <button
                      type="button"
                      className="primary-button small"
                      onClick={nextQuestion}
                      disabled={selectedAnswer === null}
                    >
                      {currentIndex === questions.length - 1 ? 'Finish' : 'Next question'}
                    </button>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <h3>Start your routing challenge</h3>
                  <p>Choose the difficulty, set the number of questions, and begin your quiz.</p>
                  <div className="quiz-toolbar">
                    <label>
                      Difficulty
                      <select value={difficulty} onChange={(event) => setDifficulty(event.target.value as typeof difficulty)}>
                        {difficultyOptions.map((level) => (
                          <option key={level} value={level}>
                            {level}
                          </option>
                        ))}
                      </select>
                    </label>

                    <label>
                      Questions
                      <select value={questionCount} onChange={(event) => setQuestionCount(Number(event.target.value))}>
                        {questionCounts.map((count) => (
                          <option key={count} value={count}>
                            {count}
                          </option>
                        ))}
                      </select>
                    </label>
                  </div>

                  <div className="mini-actions">
                    <button type="button" className="primary-button small" onClick={startQuiz}>
                      Start quiz
                    </button>
                    <button type="button" className="secondary-button" onClick={startReview}>
                      Start review
                    </button>
                    <button type="button" className="secondary-button" onClick={clearReview}>
                      Clear review
                    </button>
                  </div>
                </div>
              )}
            </article>

            <aside className="panel-card">
              <div className="card-header">
                <p className="eyebrow">Live summary</p>
                <span className="tag success">{score >= 0 ? '+' : ''}{score}</span>
              </div>

              <div className="score-ring" style={{ background: `conic-gradient(#38bdf8 0 ${Math.min(100, Math.max(0, 100 * (correctCount / Math.max(questions.length || 1, 1))))}%, rgba(148, 163, 184, 0.2) ${Math.min(100, Math.max(0, 100 * (correctCount / Math.max(questions.length || 1, 1))))}% 100%)` }}>
                <div className="score-inner">
                  <strong>{questions.length ? Math.round((correctCount / questions.length) * 100) : 0}%</strong>
                  <span>score</span>
                </div>
              </div>

              <ul className="summary-list">
                <li>
                  <span>Correct</span>
                  <strong>{correctCount}</strong>
                </li>
                <li>
                  <span>Incorrect</span>
                  <strong>{questions.length ? Math.max(0, currentIndex + 1 - correctCount) : 0}</strong>
                </li>
                <li>
                  <span>Review queue</span>
                  <strong>{reviewQueue.length}</strong>
                </li>
              </ul>
            </aside>
          </section>
        )}

        {activeTab === 'Route Lab' && (
          <section className="lab-preview">
            <div className="lab-header">
              <div>
                <p className="eyebrow">Visualization</p>
                <h3>Longest Prefix Match</h3>
              </div>
              <span className="tag neutral">Route Lab</span>
            </div>

            <div className="route-controls">
              <label>
                Destination IP
                <input value={routeDestination} onChange={(event) => setRouteDestination(event.target.value)} />
              </label>
              <label>
                Scenario
                <select value={routeScenario} onChange={(event) => loadRouteScenario(event.target.value as RouteScenarioKey)}>
                  {(Object.keys(routeLabScenarios) as RouteScenarioKey[]).map((scenario) => (
                    <option key={scenario} value={scenario}>
                      {scenario}
                    </option>
                  ))}
                </select>
              </label>
              <button type="button" className="primary-button small" onClick={analyzeRouteLab}>
                Analyze Route
              </button>
            </div>

            <div className="route-topology">
              <svg className="route-links" viewBox="0 0 720 260" preserveAspectRatio="none">
                {routeLabRoutes
                  .filter((route) => routeScenario && routeLabScenarios[routeScenario].focus.includes(route.prefix))
                  .flatMap((route) => {
                    const segments = route.path.slice(0, -1).map((nodeName, index) => {
                      const start = routeNodeMap[nodeName]
                      const end = routeNodeMap[route.path[index + 1]]
                      return {
                        x1: start.x,
                        y1: start.y,
                        x2: end.x,
                        y2: end.y,
                        color: route.color,
                      }
                    })
                    return segments
                  })
                  .map((segment, index) => (
                    <line
                      key={`${segment.x1}-${segment.y1}-${segment.x2}-${segment.y2}-${index}`}
                      x1={segment.x1}
                      y1={segment.y1}
                      x2={segment.x2}
                      y2={segment.y2}
                      stroke={segment.color}
                      strokeWidth={4}
                    />
                  ))}
              </svg>

              {routeNodes.map((node) => (
                <div
                  key={node.id}
                  className={`route-node ${node.id === 'Edge' ? 'edge' : node.id.includes('LAN') || node.id === 'Internet' ? 'lan' : 'router'}`}
                  style={{ left: `${node.x}px`, top: `${node.y}px` }}
                >
                  {node.id}
                </div>
              ))}
            </div>

            <div className="route-analysis">
              <div className="route-summary">{routeSummary}</div>
              <div className="route-detail">{routeDetail}</div>
              <table className="route-table">
                <thead>
                  <tr>
                    <th>Prefix</th>
                    <th>Protocol</th>
                    <th>AD</th>
                    <th>Metric</th>
                  </tr>
                </thead>
                <tbody>
                  {routeMatches.map((route) => (
                    <tr key={route.prefix} className={routeWinner?.prefix === route.prefix ? 'winner' : ''}>
                      <td>{route.prefix}</td>
                      <td>{route.protocol}</td>
                      <td>{route.ad}</td>
                      <td>{route.metric}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {activeTab === 'OSPF Lab' && (
          <section className="lab-preview">
            <div className="lab-header">
              <div>
                <p className="eyebrow">Area behavior</p>
                <h3>OSPF concepts</h3>
              </div>
              <span className="tag neutral">OSPF Lab</span>
            </div>

            <div className="route-controls ospf-controls">
              <label>
                Scenario
                <select value={ospfScenario} onChange={(event) => setOspfScenario(event.target.value as OSPFScenarioKey)}>
                  {(Object.keys(ospfLabScenarios) as OSPFScenarioKey[]).map((scenario) => (
                    <option key={scenario} value={scenario}>
                      {scenario}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <div className="ospf-layout">
              <div className="ospf-area area-0">
                <span>Area 0</span>
              </div>
              <div className="ospf-area area-1">
                <span>Area 1</span>
              </div>

              <div className={`ospf-node ospf-r1 ${ospfLabScenarios[ospfScenario].highlight.includes('R1') ? 'highlighted' : ''}`}>R1</div>
              <div className={`ospf-node ospf-r2 ${ospfLabScenarios[ospfScenario].highlight.includes('R2 ABR') ? 'highlighted' : ''}`}>R2 ABR</div>
              <div className={`ospf-node ospf-r3 ${ospfLabScenarios[ospfScenario].highlight.includes('R3') ? 'highlighted' : ''}`}>R3</div>
              <div className={`ospf-node ospf-r4 ${ospfLabScenarios[ospfScenario].highlight.includes('R4') ? 'highlighted' : ''}`}>R4</div>
              <div className={`ospf-node ospf-r5 ${ospfLabScenarios[ospfScenario].highlight.includes('R5') ? 'highlighted' : ''}`}>R5</div>
              <div className={`ospf-node ospf-lan0 ${ospfLabScenarios[ospfScenario].highlight.includes('LAN0') ? 'highlighted' : ''}`}>LAN0</div>
              <div className={`ospf-node ospf-lan1 ${ospfLabScenarios[ospfScenario].highlight.includes('LAN1') ? 'highlighted' : ''}`}>LAN1</div>
              <div className={`ospf-node ospf-asbr ${ospfLabScenarios[ospfScenario].highlight.includes('ASBR') ? 'highlighted' : ''}`}>ASBR</div>
            </div>

            <div className="route-analysis ospf-analysis">
              <div className="route-summary">{ospfLabScenarios[ospfScenario].summary}</div>
              <div className="route-detail">
                {Object.entries(ospfLabScenarios[ospfScenario].roles).map(([node, role]) => (
                  <div key={node} className="ospf-role">
                    <strong>{node}</strong>
                    <span>{role}</span>
                  </div>
                ))}
              </div>

              <table className="ospf-table">
                <thead>
                  <tr>
                    <th>LSA / Role</th>
                    <th>Area</th>
                    <th>Source</th>
                    <th>Meaning</th>
                  </tr>
                </thead>
                <tbody>
                  {ospfLabScenarios[ospfScenario].lsa_rows.map((row) => (
                    <tr key={`${ospfScenario}-${row.lsa}-${row.source}`}>
                      <td>{row.lsa}</td>
                      <td>{row.area}</td>
                      <td>{row.source}</td>
                      <td>{row.meaning}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}

        {activeTab === 'History' && (
          <section className="history-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Score history</p>
                <h3>Last 20 results</h3>
              </div>
            </div>

            <div className="history-list">
              {history.length ? (
                history.map((entry, index) => (
                  <div key={`${entry.date}-${index}`} className="history-entry">
                    <span>{new Date(entry.date).toLocaleString()}</span>
                    <strong>{entry.difficulty}</strong>
                    <span>{entry.score} pts</span>
                    <span>{entry.percentage}%</span>
                  </div>
                ))
              ) : (
                <div className="empty-history">No quiz history yet.</div>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default App
