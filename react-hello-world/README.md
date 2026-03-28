# React Hello World 🚀

A simple Hello World React application demonstrating fundamental React concepts with comprehensive testing and documentation.

## 📋 Overview

This project is a starter React application built with Vite, featuring:

- **Functional Components**: Modern React using hooks
- **State Management**: Counter example using `useState` hook
- **Event Handling**: Button click handlers for increment, decrement, and reset
- **CSS Styling**: Clean, responsive design
- **Testing**: Comprehensive test suite with Vitest and Testing Library

## 🛠️ Tech Stack

- **React 19** - UI library
- **Vite** - Fast build tool and dev server
- **Vitest** - Unit testing framework
- **Testing Library** - React testing utilities
- **ESLint** - Code linting

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Installation

```bash
# Navigate to project directory
cd react-hello-world

# Install dependencies
npm install
```

### Running the App

```bash
# Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### Running Tests

```bash
# Run tests in watch mode
npm run test

# Run tests with coverage
npm run test:coverage
```

## 📁 Project Structure

```
react-hello-world/
├── src/
│   ├── App.jsx          # Main application component
│   ├── App.css          # Application styles
│   ├── App.test.jsx     # Test suite for App component
│   ├── setupTests.js    # Test configuration
│   └── main.jsx         # Application entry point
├── index.html           # HTML template
├── package.json         # Dependencies and scripts
├── vite.config.js       # Vite configuration
└── vitest.config.js     # Vitest configuration
```

## 🧪 Test Coverage

The test suite includes tests for:

| Test Case | Description |
|-----------|-------------|
| `renders the Hello World heading` | Verifies main heading displays |
| `renders welcome message` | Verifies welcome text displays |
| `displays initial count of 0` | Verifies counter starts at 0 |
| `increments count` | Verifies + Increase button works |
| `decrements count` | Verifies − Decrease button works |
| `does not decrement below 0` | Verifies counter floor is 0 |
| `resets count to 0` | Verifies Reset button works |
| `renders all control buttons` | Verifies all buttons exist |

## 🔧 Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npm run test` | Run tests in watch mode |
| `npm run test:coverage` | Run tests with coverage report |
| `npm run lint` | Run ESLint |

## 📚 Key Concepts

### useState Hook

The counter demonstrates React's `useState` hook for state management:

```jsx
const [count, setCount] = useState(0)
```

### Event Handlers

Three event handlers manage counter state:

```jsx
const handleIncrement = () => setCount(c => c + 1)
const handleDecrement = () => setCount(c => Math.max(0, c - 1))
const handleReset = () => setCount(0)
```

### Accessibility

All interactive elements include proper ARIA labels:

```jsx
<button aria-label="Increment counter">+ Increase</button>
```

## 📄 License

MIT License - feel free to use this as a starter for your own projects!

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with ❤️ using React + Vite