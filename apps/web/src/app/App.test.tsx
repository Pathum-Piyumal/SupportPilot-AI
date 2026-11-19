import { render, screen, cleanup } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, expect, it } from 'vitest';
import { App } from './App';
afterEach(cleanup);
it('identifies the demo and does not claim working predictions', () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );
  expect(
    screen.getByRole('heading', { name: 'SupportPilot AI' }),
  ).toBeInTheDocument();
  expect(screen.getByText(/not yet available/)).toBeInTheDocument();
});
it('provides a route back from unknown pages', () => {
  render(
    <MemoryRouter initialEntries={['/missing']}>
      <App />
    </MemoryRouter>,
  );
  expect(screen.getByRole('link', { name: 'Return home' })).toHaveAttribute(
    'href',
    '/',
  );
});
