import { Link, Route, Routes } from 'react-router-dom';
export function App() {
  return (
    <Routes>
      <Route
        path="/"
        element={
          <main>
            <p>Development foundation</p>
            <h1>SupportPilot AI</h1>
            <p>
              A customer-support workspace for reviewing intent predictions and
              evidence-grounded drafts.
            </p>
            <p>This is a fictional banking demo using synthetic data.</p>
            <p>
              Ticket workflows, classification, retrieval, and drafting are
              planned and not yet available.
            </p>
          </main>
        }
      />
      <Route
        path="*"
        element={
          <main>
            <h1>Page not found</h1>
            <Link to="/">Return home</Link>
          </main>
        }
      />
    </Routes>
  );
}
