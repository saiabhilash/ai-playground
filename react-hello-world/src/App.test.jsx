import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from './App'

/**
 * Test Suite for App Component
 * 
 * These tests verify the functionality of the Hello World React application:
 * - Initial render and content
 * - Counter functionality (increment, decrement, reset)
 * - Accessibility attributes
 * - User interactions
 */
describe('App', () => {
  /**
   * Test: Renders the main heading
   * Verifies that the "Hello World" heading is displayed
   */
  it('renders the Hello World heading', () => {
    render(<App />)
    const heading = screen.getByText(/hello world/i)
    expect(heading).toBeInTheDocument()
  })

  /**
   * Test: Renders welcome message
   * Verifies the welcome paragraph is displayed
   */
  it('renders welcome message', () => {
    render(<App />)
    const welcomeText = screen.getByText(/welcome to your first react application/i)
    expect(welcomeText).toBeInTheDocument()
  })

  /**
   * Test: Counter starts at 0
   * Verifies the initial counter value is 0
   */
  it('displays initial count of 0', () => {
    render(<App />)
    const countDisplay = screen.getByText('Count: 0')
    expect(countDisplay).toBeInTheDocument()
  })

  /**
   * Test: Increment button increases count
   * Verifies clicking + Increase updates the count
   */
  it('increments count when + Increase button is clicked', () => {
    render(<App />)
    
    // Initial count is 0
    expect(screen.getByText('Count: 0')).toBeInTheDocument()
    
    // Click increment button
    const incrementBtn = screen.getByRole('button', { name: /increment counter/i })
    fireEvent.click(incrementBtn)
    
    // Count should now be 1
    expect(screen.getByText('Count: 1')).toBeInTheDocument()
  })

  /**
   * Test: Decrement button decreases count
   * Verifies clicking − Decrease updates the count
   */
  it('decrements count when − Decrease button is clicked', () => {
    render(<App />)
    
    // First increment to 3
    const incrementBtn = screen.getByRole('button', { name: /increment counter/i })
    fireEvent.click(incrementBtn)
    fireEvent.click(incrementBtn)
    fireEvent.click(incrementBtn)
    expect(screen.getByText('Count: 3')).toBeInTheDocument()
    
    // Then decrement
    const decrementBtn = screen.getByRole('button', { name: /decrement counter/i })
    fireEvent.click(decrementBtn)
    
    expect(screen.getByText('Count: 2')).toBeInTheDocument()
  })

  /**
   * Test: Count does not go below 0
   * Verifies decrementing below 0 stays at 0
   */
  it('does not decrement below 0', () => {
    render(<App />)
    
    // Initial count is 0
    expect(screen.getByText('Count: 0')).toBeInTheDocument()
    
    // Try to decrement
    const decrementBtn = screen.getByRole('button', { name: /decrement counter/i })
    fireEvent.click(decrementBtn)
    
    // Count should still be 0
    expect(screen.getByText('Count: 0')).toBeInTheDocument()
  })

  /**
   * Test: Reset button sets count to 0
   * Verifies clicking Reset returns count to 0
   */
  it('resets count to 0 when Reset button is clicked', () => {
    render(<App />)
    
    // First increment to 5
    const incrementBtn = screen.getByRole('button', { name: /increment counter/i })
    for (let i = 0; i < 5; i++) {
      fireEvent.click(incrementBtn)
    }
    expect(screen.getByText('Count: 5')).toBeInTheDocument()
    
    // Click reset
    const resetBtn = screen.getByRole('button', { name: /reset counter/i })
    fireEvent.click(resetBtn)
    
    expect(screen.getByText('Count: 0')).toBeInTheDocument()
  })

  /**
   * Test: All three buttons are present
   * Verifies all control buttons exist and are accessible
   */
  it('renders all three control buttons', () => {
    render(<App />)
    
    expect(screen.getByRole('button', { name: /decrement counter/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /reset counter/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /increment counter/i })).toBeInTheDocument()
  })

  /**
   * Test: Counter section exists
   * Verifies the counter section heading is present
   */
  it('renders the counter section heading', () => {
    render(<App />)
    const sectionHeading = screen.getByRole('heading', { name: /counter example/i })
    expect(sectionHeading).toBeInTheDocument()
  })

  /**
   * Test: Info section exists
   * Verifies the getting started section is present
   */
  it('renders the getting started section', () => {
    render(<App />)
    const infoHeading = screen.getByRole('heading', { name: /getting started/i })
    expect(infoHeading).toBeInTheDocument()
  })
})