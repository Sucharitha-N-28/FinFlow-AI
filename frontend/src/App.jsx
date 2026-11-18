
import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import {
  LayoutDashboard,
  FileText,
  History,
  CircleHelp,
  UploadCloud,
  X,
  CheckCircle2,
  BarChart3,

  Building2,
  Scale,
  FileSearch,
  ListChecks,
  Settings,
  Sparkles,
  Play,
  Table2,
  FileChartColumn,
  Info,
 
} from 'lucide-react'
import './App.css'

const API_URL = 'http://localhost:8000/api/v1/upload'

const MODULE_NAMES = {
  extraction: 'Extraction',
  classification: 'Classification',
  summarization: 'Summarization',
  question_answering: 'Question Answering',
  comparison: 'Comparison',
}



function App() {
  const [prompt, setPrompt] = useState('')
  const [files, setFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)
  const [history, setHistory] = useState([])
  const [activePage, setActivePage] = useState('analyze')
  const [activeTab, setActiveTab] = useState('comparison')

  const steps = result?.orchestration_result?.steps_executed || []
  const detectedIntents =
    result?.orchestration_result?.detected_intents || []

  const extractionStep = steps.find(
    (step) => step.intent === 'extraction'
  )

  const extractedDocuments = Array.isArray(extractionStep?.result)
    ? extractionStep.result
    : []

  const formatFileSize = (size) => {
    if (!size) return ''
    return size < 1024 * 1024
      ? `${(size / 1024).toFixed(0)} KB`
      : `${(size / (1024 * 1024)).toFixed(2)} MB`
  }

  const handleFileChange = (event) => {
    const selected = Array.from(event.target.files || [])
    setFiles((previous) => {
      const combined = [...previous]
      selected.forEach((file) => {
        if (
          !combined.some(
            (existing) =>
              existing.name === file.name &&
              existing.size === file.size
          )
        ) {
          combined.push(file)
        }
      })
      return combined.slice(0, 5)
    })
    setResult(null)
    setError('')
    event.target.value = ''
  }

  const handleDrop = (event) => {
    event.preventDefault()
    const dropped = Array.from(event.dataTransfer.files || [])
    setFiles((previous) => {
      const combined = [...previous]
      dropped.forEach((file) => {
        if (
          !combined.some(
            (existing) =>
              existing.name === file.name &&
              existing.size === file.size
          )
        ) {
          combined.push(file)
        }
      })
      return combined.slice(0, 5)
    })
    setResult(null)
    setError('')
  }

  const removeFile = (index) => {
    setFiles((previous) => previous.filter((_, i) => i !== index))
  }

  const handleSubmit = async (event) => {
    event.preventDefault()

    if (!prompt.trim()) {
      setError('Please enter your instructions.')
      return
    }

    if (files.length === 0) {
      setError('Please upload at least one document.')
      return
    }

    const formData = new FormData()
    formData.append('prompt', prompt)
    files.forEach((file) => formData.append('files', file))

    try {
      setLoading(true)
      setError('')
      setResult(null)
      setActiveTab('comparison')

      const response = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail || data)
        )
      }

      setResult(data)
setActivePage('analyze')

const completedIntents =
  data?.orchestration_result?.detected_intents || []

if (completedIntents.includes('comparison')) {
  setActiveTab('comparison')
}else if (completedIntents.includes('classification')) {
  setActiveTab('classification')
} else if (completedIntents.includes('question_answering')) {
  setActiveTab('qa')
} else if (completedIntents.includes('extraction')) {
  setActiveTab('extraction')
} else {
  setActiveTab('details')
}

      setHistory((previous) => [
        {
          id: Date.now(),
          prompt,
          fileNames: files.map((file) => file.name),
          data,
          createdAt: new Date().toLocaleString(),
        },
        ...previous,
      ])
    } catch (err) {
      setError(err.message || 'Unable to connect to the backend.')
    } finally {
      setLoading(false)
    }
  }

  const renderMarkdown = (content) => (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        table: ({ children, ...props }) => (
          <div className="table-scroll">
            <table {...props}>{children}</table>
          </div>
        ),
      }}
    >
      {String(content || '')}
    </ReactMarkdown>
  )

  const renderFinancialData = (financialData) => {
    if (!financialData) {
      return <p>No structured financial data available.</p>
    }

    return (
      <div className="detail-grid">
        {Object.entries(financialData).map(([key, value]) => (
          <div className="detail-item" key={key}>
            <span>{key.replaceAll('_', ' ')}</span>
            <strong>
              {value === null || value === undefined || value === ''
                ? 'Not available'
                : String(value)}
            </strong>
          </div>
        ))}
      </div>
    )
  }

  const renderExtractionResults = () => {
    if (!extractedDocuments.length) {
      return <EmptyState message="No extraction results are available for this request." />
    }

    return extractedDocuments.map((item, index) => (
      <div className="document-result-card" key={index}>
        <div className="document-result-heading">
          <FileText size={21} />
          <div>
            <h3>{item.file_name}</h3>
            <span>Extracted financial information</span>
          </div>
        </div>
        {renderFinancialData(item.financial_data)}
      </div>
    ))
  }
  const renderClassificationResults = () => {
  const classificationStep = steps.find(
    (step) => step.intent === 'classification'
  )

  if (
    !classificationStep ||
    !Array.isArray(classificationStep.result) ||
    classificationStep.result.length === 0
  ) {
    return (
      <EmptyState message="No classification results are available for this request." />
    )
  }

  return classificationStep.result.map((item, index) => (
    <div className="document-result-card" key={index}>
      <div className="document-result-heading">
        <FileSearch size={22} />
        <div>
          <h3>{item.file_name}</h3>
          <span>Document classification</span>
        </div>
      </div>

      <div className="detail-grid">
        <div className="detail-item">
          <span>Document category</span>
          <strong>{item.category || 'Not available'}</strong>
        </div>
      </div>
    </div>
  ))
}

 
const renderSummaries = () => {
  const summaryStep = steps.find(
    (step) => step.intent === 'summarization'
  )

  if (!summaryStep || !Array.isArray(summaryStep.result)) {
    return (
      <EmptyState message="No summaries are available for this request." />
    )
  }

  return summaryStep.result.map((item, index) => (
    <div className="document-result-card" key={index}>
      <h3>{item.file_name}</h3>
      <div className="markdown-content">
        {renderMarkdown(
          item.summary || item.answer || 'Summary content is unavailable.'
        )}
      </div>
    </div>
  ))
}

const renderQuestionAnswers = () => {
  const qaStep = steps.find(
    (step) => step.intent === 'question_answering'
  )

  if (!qaStep || !Array.isArray(qaStep.result) || qaStep.result.length === 0) {
    return (
      <EmptyState message="No question answers are available for this request." />
    )
  }

  return qaStep.result.map((item, index) => (
    <div className="document-result-card" key={index}>
      <h3>{item.file_name}</h3>
      <div className="markdown-content">
        {renderMarkdown(item.answer)}
      </div>
    </div>
  ))
}


  const renderComparison = () => {
    const comparisonStep = steps.find(
      (step) => step.intent === 'comparison'
    )

    if (!comparisonStep) {
      return (
        <EmptyState message="Run a document comparison to view the comparison report." />
      )
    }

    const content =
      typeof comparisonStep.result === 'string'
        ? comparisonStep.result
        : JSON.stringify(comparisonStep.result, null, 2)

    return (
      <div className="comparison-layout">
        <div className="comparison-main">
          <div className="section-heading">
            <Scale size={23} />
            <h3>Financial Document Comparison</h3>
          </div>
          <div className="markdown-content comparison-markdown">
            {renderMarkdown(content)}
          </div>
        </div>
      </div>
    )
  }

  const renderDocumentDetails = () => {
    if (!extractedDocuments.length) {
      return <EmptyState message="Document details will appear after extraction." />
    }

    return (
      <div className="document-details-list">
        {extractedDocuments.map((item, index) => (
          <div className="document-result-card" key={index}>
            <div className="document-result-heading">
              <FileSearch size={22} />
              <div>
                <h3>{item.file_name}</h3>
                <span>Document metadata and financial information</span>
              </div>
            </div>
            {renderFinancialData(item.financial_data)}
          </div>
        ))}
      </div>
    )
  }



  const renderExecutionSteps = () => {
    if (!steps.length) {
      return (
        <EmptyState message="Execution steps will appear after analysis." />
      )
    }

    return (
      <div className="execution-flow">
        {steps.map((step, index) => {
          const Icon =
            step.intent === 'extraction'
              ? FileText
              : step.intent === 'classification'
                ? Building2
                : step.intent === 'summarization'
                  ? FileChartColumn
                  : step.intent === 'comparison'
                    ? BarChart3
                    : FileSearch

          return (
            <div className="execution-item" key={index}>
              <div className="execution-number">{index + 1}</div>
              <Icon size={27} className="execution-icon" />
              <div className="execution-info">
                <strong>
                  {MODULE_NAMES[step.intent] || step.intent}
                </strong>
                <span>{step.module}</span>
                <small>{step.model}</small>
                <div className="completed-label">
                  <CheckCircle2 size={14} />
                  Completed
                </div>
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  const renderHistory = () => (
    <div className="page-content">
      <div className="page-title">
        <History size={26} />
        <div>
          <h2>Analysis History</h2>
          <p>Your recent document analysis requests in this session.</p>
        </div>
      </div>

      {history.length === 0 ? (
        <EmptyState message="No analysis history yet. Your completed requests will appear here." />
      ) : (
        <div className="history-list">
          {history.map((item) => (
            <div className="history-card" key={item.id}>
              <div>
                <h3>{item.fileNames.join(', ')}</h3>
                <p>{item.prompt}</p>
                <small>{item.createdAt}</small>
              </div>
              <button
                className="secondary-button"
                onClick={() => {
  setResult(item.data)
  setPrompt(item.prompt)
  setActivePage('analyze')

  const savedIntents =
    item.data?.orchestration_result?.detected_intents || []

  if (savedIntents.includes('comparison')) {
    setActiveTab('comparison')
  }else if (savedIntents.includes('classification')) {
    setActiveTab('classification')
  } else if (savedIntents.includes('question_answering')) {
    setActiveTab('qa')
  } else if (savedIntents.includes('extraction')) {
    setActiveTab('extraction')
  } else {
    setActiveTab('details')
  }
}}
              >
                View Results
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )

  const renderHowItWorks = () => (
    <div className="page-content">
      <div className="page-title">
        <ListChecks size={26} />
        <div>
          <h2>How FinFlow AI Works</h2>
          <p>Understand the financial document processing workflow.</p>
        </div>
      </div>

      <div className="how-grid">
        {[
          ['01', 'Upload Documents', 'Upload supported financial PDF, TXT or image documents.'],
          ['02', 'Intent Detection', 'The system identifies the requested financial tasks.'],
          ['03', 'Task Planning', 'The orchestrator determines task dependencies and execution order.'],
          ['04', 'Model Routing', 'Tasks are assigned to suitable local Ollama models.'],
          ['05', 'Processing', 'Extraction, classification, summarization, QA and comparison modules execute.'],
          ['06', 'View Results', 'Review structured financial information and analysis reports.'],
        ].map(([number, title, description]) => (
          <div className="how-card" key={number}>
            <span>{number}</span>
            <h3>{title}</h3>
            <p>{description}</p>
          </div>
        ))}
      </div>
    </div>
  )

  const renderHelp = () => (
    <div className="page-content">
      <div className="page-title">
        <CircleHelp size={26} />
        <div>
          <h2>Help & Information</h2>
          <p>Guidance for using FinFlow AI.</p>
        </div>
      </div>

      <div className="help-card">
        <h3>Supported document formats</h3>
        <p>PDF, TXT, PNG, JPG and JPEG.</p>
        <h3>Available operations</h3>
        <ul>
          <li>Financial information extraction</li>
          <li>Document classification</li>
          <li>Financial document summarization</li>
          <li>Financial question answering</li>
          <li>Multi-document comparison</li>
        </ul>
        <h3>Example instruction</h3>
        <p>
          "Compare the financial performance of these two companies and
          identify differences in revenue, expenses and net profit."
        </p>
      </div>
    </div>
  )

  const navigation = [
    { id: 'analyze', label: 'Analyze Documents', icon: LayoutDashboard },
    { id: 'history', label: 'Results History', icon: History },
    { id: 'how', label: 'How It Works', icon: ListChecks },
    { id: 'help', label: 'Help', icon: CircleHelp },
  ]

  return (
    <div className="dashboard">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Building2 size={27} />
          </div>
          <div>
            <h1>FinFlow AI</h1>
            <p>Intelligent Financial Document Processing</p>
          </div>
        </div>

        
      </header>

      <div className="dashboard-body">
        <aside className="sidebar">
          <nav>
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <button
                  key={item.id}
                  className={`nav-item ${activePage === item.id ? 'active' : ''}`}
                  onClick={() => setActivePage(item.id)}
                >
                  <Icon size={20} />
                  <span>{item.label}</span>
                </button>
              )
            })}
          </nav>

          <div className="sidebar-footer">
            <div className="sidebar-footer-icon">
              <Sparkles size={18} />
            </div>
            <strong>FinFlow AI</strong>
            <span>Local AI financial assistant</span>
          </div>
        </aside>

        <main className="dashboard-main">
          {activePage === 'analyze' && (
            <div className="workspace">
              <section className="upload-panel">
                <div className="panel-heading">
                  <FileText size={28} />
                  <div>
                    <h2>Financial Document Analysis</h2>
                    <p>
                      Upload financial documents and provide instructions
                      to extract, classify, summarize, compare or ask questions.
                    </p>
                  </div>
                </div>

                <form onSubmit={handleSubmit}>
                  <div className="form-section">
                    <label>
                      <span className="section-number">1</span>
                      Enter Your Instructions
                    </label>
                    <textarea
                      value={prompt}
                      onChange={(event) => setPrompt(event.target.value)}
                      maxLength={500}
                      placeholder="Example: Compare revenue, expenses, net profit, assets and liabilities..."
                    />
                    <div className="character-count">
                      {prompt.length} / 500
                    </div>
                  </div>

                  <div className="form-section">
                    <label>
                      <span className="section-number">2</span>
                      Upload Financial Documents
                    </label>

                    <label
                      className="drop-zone"
                      onDragOver={(event) => event.preventDefault()}
                      onDrop={handleDrop}
                    >
                      <input
                        type="file"
                        accept=".pdf,.txt,.png,.jpg,.jpeg"
                        multiple
                        onChange={handleFileChange}
                      />
                      <UploadCloud size={43} />
                      <strong>Drag and drop files here</strong>
                      <span>or click to browse</span>
                      <small>Supported: PDF, TXT, PNG, JPG, JPEG</small>
                    </label>

                    {files.length > 0 && (
                      <div className="selected-files">
                        {files.map((file, index) => (
                          <div className="file-row" key={`${file.name}-${index}`}>
                            <div className="pdf-icon">
                              <FileText size={18} />
                            </div>
                            <div className="file-info">
                              <strong>{file.name}</strong>
                              <span>{formatFileSize(file.size)}</span>
                            </div>
                            <CheckCircle2
                              className="file-check"
                              size={19}
                            />
                            <button
                              type="button"
                              className="remove-file"
                              onClick={() => removeFile(index)}
                              aria-label={`Remove ${file.name}`}
                            >
                              <X size={19} />
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {error && (
                    <div className="error-message">
                      <Info size={17} />
                      {error}
                    </div>
                  )}

                  <button
                    type="submit"
                    className="analyze-button"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="loading-spinner" />
                        Analyzing Documents...
                      </>
                    ) : (
                      <>
                        <Play size={19} />
                        Analyze Documents
                      </>
                    )}
                  </button>
                </form>
              </section>

              <section className="results-workspace">
                <div className="results-heading">
                  <div>
                    <BarChart3 size={26} />
                    <div>
                      <h2>Analysis Results</h2>
                      <p>Financial insights generated from uploaded documents</p>
                    </div>
                  </div>
                  <span
                    className={`request-status ${result?.status === 'completed' ? 'success' : ''}`}
                  >
                    <CheckCircle2 size={17} />
                    {result ? `Request Status: ${result.status}` : 'Awaiting Analysis'}
                  </span>
                </div>

                

                {result?.status === 'unsupported' ? (
                  <div className="report-panel">
                    <div className="error-message">
                      <Info size={20} />
                      <div>
                        <h3>Request Not Supported</h3>
                        <p>
                          Your request is outside FinFlow AI's supported operations.
                        </p>
                        <p>Currently supported operations:</p>
                        <ul>
                          <li>Financial information extraction</li>
                          <li>Document classification</li>
                          <li>Financial document summarization</li>
                          <li>Financial question answering</li>
                          <li>Multi-document comparison</li>
                        </ul>
                        <p>
                          Please enter an instruction related to financial document analysis.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <>
                <section className="execution-panel">
                  <div className="section-heading">
                    <Settings size={22} />
                    <h3>Execution Steps</h3>
                  </div>
                  {renderExecutionSteps()}
                </section>

                <section className="report-panel">
                  
<div className="result-tabs">
  <button
    className={activeTab === 'comparison' ? 'selected' : ''}
    onClick={() => setActiveTab('comparison')}
  >
    <BarChart3 size={17} />
    Comparison Report
  </button>

  <button
    className={activeTab === 'extraction' ? 'selected' : ''}
    onClick={() => setActiveTab('extraction')}
  >
    <Table2 size={17} />
    Extraction Results
  </button>
  <button
  className={activeTab === 'classification' ? 'selected' : ''}
  onClick={() => setActiveTab('classification')}
>
  <FileSearch size={17} />
  Classification Results
</button>


  <button
    className={activeTab === 'details' ? 'selected' : ''}
    onClick={() => setActiveTab('details')}
  >
    <FileSearch size={17} />
    Document Details
  </button>

  <button
    className={activeTab === 'qa' ? 'selected' : ''}
    onClick={() => setActiveTab('qa')}
  >
    <FileSearch size={17} />
    Question Answers
  </button>
</div>

<div className="tab-content">
  {activeTab === 'comparison' && renderComparison()}
  {activeTab === 'extraction' && renderExtractionResults()}
  {activeTab === 'classification' && renderClassificationResults()}
  {activeTab === 'details' && renderDocumentDetails()}
  {activeTab === 'qa' && renderQuestionAnswers()}
</div>

                </section>

                {steps.some((step) => step.intent === 'summarization') && (
                  <section className="report-panel summary-panel">
                    <div className="section-heading">
                      <FileChartColumn size={22} />
                      <h3>Document Summaries</h3>
                    </div>
                    {renderSummaries()}
                  </section>
                )}

                                {detectedIntents.length > 0 && (
                  <div className="detected-intents">
                    <strong>Detected tasks</strong>
                    <div>
                      {detectedIntents.map((intent, index) => (
                        <span key={`${intent}-${index}`}>
                          {MODULE_NAMES[intent] || intent}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                  </>
                )}
              </section>
            </div>
          )}

          {activePage === 'history' && renderHistory()}
          {activePage === 'how' && renderHowItWorks()}
          {activePage === 'help' && renderHelp()}
        </main>
      </div>
    </div>
  )
}

function EmptyState({ message }) {
  return (
    <div className="empty-state">
      <FileSearch size={34} />
      <p>{message}</p>
    </div>
  )
}

export default App
