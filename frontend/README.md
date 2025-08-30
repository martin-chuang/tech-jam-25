# AI Chat Interface

A modern, production-ready React chat interface built with TypeScript, featuring file uploads, real-time streaming, and a clean UI inspired by popular AI chat applications.

## Features

- 🎨 **Modern UI** - Clean, dark theme inspired by ChatGPT and Gemini
- 📁 **File Upload** - Support for multiple file types with drag & drop
- ⚡ **SSE Streaming** - Real-time streaming responses from AI backend
- 📱 **Responsive** - Mobile-first design with adaptive layout
- 🔧 **TypeScript** - Full type safety and excellent developer experience
- 🧪 **Testing** - Comprehensive test suite with Vitest and React Testing Library
- 🎯 **Production Ready** - Optimized builds and error boundaries

## Supported File Types

- Text files (.txt, .md, .csv, .json)
- Images (.jpg, .jpeg, .png, .gif, .webp)
- Documents (.pdf, .doc, .docx)
- Max file size: 10MB per file

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Testing**: Vitest + React Testing Library
- **Linting**: ESLint + TypeScript ESLint

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-chat-interface
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment variables:
```bash
cp .env.example .env
```

4. Update the `.env` file with your API endpoint:
```env
VITE_API_URL=http://localhost:3001
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### Building for Production

Build the application:
```bash
npm run build
```

Preview the production build:
```bash
npm run preview
```

## Testing

Run tests:
```bash
npm run test
```

Run tests with coverage:
```bash
npm run test:coverage
```

Run tests with UI:
```bash
npm run test:ui
```

## Backend API

The frontend expects a backend API with the following endpoints:

### POST /api/chat

Send a chat message with optional file attachments.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body:
  - `message` (string): The chat message
  - `sessionId` (string): Session identifier
  - `file-*` (File[]): Optional file attachments

**Response:**
Server-Sent Events stream with the format:
```
data: {"content": "streaming response chunk"}
data: {"content": " more content"}
data: [DONE]
```

**Error Response:**
```
data: {"error": "Error message"}
```

### Example Backend Implementation (Node.js/Express)

```javascript
app.post('/api/chat', upload.array('files'), (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Access-Control-Allow-Origin': '*',
  })

  // Process the message and files
  const { message, sessionId } = req.body
  const files = req.files
  
  // Stream response chunks
  const response = "This is a streaming response..."
  for (let i = 0; i < response.length; i += 10) {
    const chunk = response.slice(i, i + 10)
    res.write(`data: ${JSON.stringify({ content: chunk })}\\n\\n`)
  }
  
  res.write('data: [DONE]\\n\\n')
  res.end()
})
```

## Project Structure

```
src/
├── components/          # React components
│   ├── ChatMessage.tsx  # Individual message component
│   ├── ChatInput.tsx    # Message input with file upload
│   ├── ChatWindow.tsx   # Main chat interface
│   ├── FileUpload.tsx   # File upload component
│   ├── Sidebar.tsx      # Session management sidebar
│   └── ErrorBoundary.tsx # Error boundary component
├── hooks/               # Custom React hooks
│   ├── useChat.ts       # Chat state management
│   └── useFileUpload.ts # File upload logic
├── types/               # TypeScript type definitions
│   ├── chat.ts          # Chat-related types
│   └── api.ts           # API-related types
├── utils/               # Utility functions
│   ├── file-validation.ts # File validation logic
│   ├── error-handler.ts   # Error handling utilities
│   └── cn.ts              # Class name utilities
└── test/                # Test configuration
    └── setup.ts         # Test setup file
```

## Key Features Explained

### File Upload System
- Drag & drop support with visual feedback
- Client-side validation (file type and size)
- Real-time file preview with remove functionality
- Base64 encoding for text files, data URLs for images

### Streaming Responses
- Server-Sent Events (SSE) for real-time streaming
- Proper error handling and connection management
- Visual streaming indicator with typing animation
- Ability to stop generation mid-stream

### Session Management
- Multiple chat sessions with persistence
- Automatic title generation from first message
- Session switching with message history
- Delete sessions (with protection for last session)

### Error Handling
- Comprehensive error boundary for React errors
- API error handling with user-friendly messages
- Network error detection and retry logic
- Validation errors for file uploads

### Responsive Design
- Mobile-first approach with collapsible sidebar
- Touch-friendly interface elements
- Adaptive layouts for different screen sizes
- Accessible keyboard navigation

## Configuration

### Environment Variables

- `VITE_API_URL` - Backend API endpoint
- `VITE_ANALYTICS_ID` - Optional analytics tracking ID
- `VITE_SENTRY_DSN` - Optional error reporting DSN

### Customization

The app uses CSS custom properties for theming. Main theme colors are defined in `tailwind.config.js`:

```javascript
colors: {
  'chat': {
    'bg': '#0d1117',        // Background
    'surface': '#161b22',   // Cards/surfaces
    'border': '#30363d',    // Borders
    'text': '#f0f6fc',      // Primary text
    'text-secondary': '#8b949e', // Secondary text
    'accent': '#238636',    // Accent color
    'error': '#f85149',     // Error color
    'warning': '#d29922'    // Warning color
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.