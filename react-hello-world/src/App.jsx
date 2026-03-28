import { useState } from 'react'
import './App.css'

/**
 * App Component - Hello World React Application
 * 
 * A simple counter application demonstrating React fundamentals:
 * - Functional components
 * - useState hook for state management
 * - Event handling
 * - CSS styling
 * 
 * @returns {JSX.Element} The rendered App component
 */
function App() {
  const [count, setCount] = useState(0)

  const handleIncrement = () => setCount(c => c + 1)
  const handleDecrement = () => setCount(c => Math.max(0, c - 1))
  const handleReset = () => setCount(0)

  return (
    <div className="app">
      <header className="app-header">
        <h1>Hello World! 👋</h1>
        <p>Welcome to your first React application</p>
      </header>

      <main className="app-main">
        <section className="counter-section">
          <h2>Counter Example</h2>
          <p className="count-display">Count: {count}</p>
          <div className="button-group">
            <button 
              className="btn btn-decrement" 
              onClick={handleDecrement}
              aria-label="Decrement counter"
            >
              − Decrease
            </button>
            <button 
              className="btn btn-reset" 
              onClick={handleReset}
              aria-label="Reset counter"
            >
              Reset
            </button>
            <button 
              className="btn btn-increment" 
              onClick={handleIncrement}
              aria-label="Increment counter"
            >
              + Increase
            </button>
          </div>
        </section>

        <section className="info-section">
          <h3>Getting Started</h3>
          <ul>
            <li>Edit <code>src/App.jsx</code> to modify this component</li>
            <li>Edit <code>src/App.css</code> to change styles</li>
            <li>Run <code>npm run dev</code> for development server</li>
            <li>Run <code>npm run test</code> to execute tests</li>
          </ul>
        </section>
      </main>

      <footer className="app-footer">
        <p>Built with React + Vite | Count: {count}</p>
      </footer>
    </div>
  )
}

export default App