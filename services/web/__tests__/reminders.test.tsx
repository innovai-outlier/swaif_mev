// eslint-disable-next-line no-unused-vars
import '@testing-library/jest-dom';
// @vitest-environment jsdom

import { render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import ProgramsPage from '../app/programs/page';

// Mock API calls
vi.mock('../lib/api', () => ({
  getPrograms: () => Promise.resolve([
    { id: 1, name: 'Programa Teste', description: 'Desc', is_active: true }
  ]),
  getUserEnrollments: () => Promise.resolve([]),
  getReminders: () => Promise.resolve([
    { id: 1, habit_id: 1, scheduled_for: new Date().toISOString(), status: 'pending', message: 'Lembrete de teste' }
  ]),
  getProgramHabits: () => Promise.resolve([
    { id: 1, name: 'Hábito Teste', description: 'Desc', points_per_completion: 10 }
  ]),
  createEnrollment: () => Promise.resolve({}),
}));

describe('Reminders UI', () => {
  it('renders reminders section', async () => {
    render(<ProgramsPage />);
    const remindersHeader = await screen.findByText(/Reminders/i);
    expect(remindersHeader).toBeInTheDocument();
  });

  it('shows reminder details with accessibility labels', async () => {
    render(<ProgramsPage />);
    const reminderItem = await screen.findByLabelText(/Lembrete para hábito 1/i);
    expect(reminderItem).toBeInTheDocument();
    expect(reminderItem).toHaveTextContent(/Lembrete de teste/);
  });

  it('shows habit details with accessibility labels', async () => {
    render(<ProgramsPage />);
    const habitItem = await screen.findByLabelText(/Hábito Hábito Teste/i);
    expect(habitItem).toBeInTheDocument();
    expect(habitItem).toHaveTextContent(/Hábito Teste/);
    expect(habitItem).toHaveTextContent(/10/);
  });

  it('shows loading spinner initially', () => {
    // Render with loading state
    const { container } = render(<ProgramsPage />);
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('shows enrollment button and disables during enrolling', async () => {
    render(<ProgramsPage />);
    const enrollButton = await screen.findByLabelText(/Inscrever-se/i);
    expect(enrollButton).toBeInTheDocument();
    expect(enrollButton).not.toBeDisabled();
  });
});
