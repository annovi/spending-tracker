import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import { ExpenseChart } from './ExpenseChart'

describe('ExpenseChart', () => {
  it('should render chart title', () => {
    const mockData = [
      { month: '2024-01', income: 5000, expense: 3000, net: 2000 },
      { month: '2024-02', income: 5500, expense: 3200, net: 2300 },
    ]

    const { getByText } = render(<ExpenseChart data={mockData} />)

    expect(getByText('Monthly Income & Expenses')).toBeInTheDocument()
  })

  it('should render with empty data', () => {
    const { getByText } = render(<ExpenseChart data={[]} />)

    expect(getByText('Monthly Income & Expenses')).toBeInTheDocument()
  })

  it('should display chart description', () => {
    const mockData = [
      { month: '2024-01', income: 5000, expense: 3000, net: 2000 },
    ]

    const { getByText } = render(<ExpenseChart data={mockData} />)

    expect(getByText(/Track your income and expenses over time/i)).toBeInTheDocument()
  })
})
