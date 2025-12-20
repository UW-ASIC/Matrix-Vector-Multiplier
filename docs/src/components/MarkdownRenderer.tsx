interface MarkdownRendererProps {
  content: string
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const renderLine = (line: string, index: number) => {
    const trimmed = line.trim()

    // Headers
    if (trimmed.startsWith('# ')) {
      return <h1 key={index}>{trimmed.slice(2)}</h1>
    }
    if (trimmed.startsWith('## ')) {
      return <h2 key={index}>{trimmed.slice(3)}</h2>
    }
    if (trimmed.startsWith('### ')) {
      return <h3 key={index}>{trimmed.slice(4)}</h3>
    }

    // Code blocks
    if (trimmed.startsWith('```')) {
      return null // Handle in paragraph processing
    }

    // Lists
    if (trimmed.startsWith('- ')) {
      return <li key={index}>{processInlineMarkdown(trimmed.slice(2))}</li>
    }
    if (trimmed.match(/^\d+\.\s/)) {
      return <li key={index}>{processInlineMarkdown(trimmed.replace(/^\d+\.\s/, ''))}</li>
    }

    // Bold
    if (trimmed.startsWith('**') || trimmed.includes('**')) {
      return <p key={index}>{processInlineMarkdown(trimmed)}</p>
    }

    // Regular paragraph
    if (trimmed) {
      return <p key={index}>{processInlineMarkdown(trimmed)}</p>
    }

    return <br key={index} />
  }

  const processInlineMarkdown = (text: string): React.ReactNode => {
    const parts: React.ReactNode[] = []
    let currentIndex = 0

    // Process inline code `code`
    const codeRegex = /`([^`]+)`/g
    let match

    while ((match = codeRegex.exec(text)) !== null) {
      // Add text before code
      if (match.index > currentIndex) {
        const beforeText = text.slice(currentIndex, match.index)
        parts.push(processBold(beforeText))
      }

      // Add code
      parts.push(<code key={match.index}>{match[1]}</code>)
      currentIndex = match.index + match[0].length
    }

    // Add remaining text
    if (currentIndex < text.length) {
      parts.push(processBold(text.slice(currentIndex)))
    }

    return parts.length > 0 ? parts : text
  }

  const processBold = (text: string): React.ReactNode => {
    const parts = text.split('**')
    return parts.map((part, i) =>
      i % 2 === 0 ? part : <strong key={i}>{part}</strong>
    )
  }

  const lines = content.trim().split('\n')
  const elements: React.ReactNode[] = []
  let inCodeBlock = false
  let codeLines: string[] = []
  let codeLang = ''

  lines.forEach((line, index) => {
    if (line.trim().startsWith('```')) {
      if (!inCodeBlock) {
        inCodeBlock = true
        codeLang = line.trim().slice(3)
        codeLines = []
      } else {
        inCodeBlock = false
        elements.push(
          <pre key={`code-${index}`}>
            <code className={codeLang ? `language-${codeLang}` : ''}>
              {codeLines.join('\n')}
            </code>
          </pre>
        )
      }
    } else if (inCodeBlock) {
      codeLines.push(line)
    } else {
      elements.push(renderLine(line, index))
    }
  })

  return <div className="markdown-content">{elements}</div>
}
