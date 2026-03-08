import { createRoot } from 'react-dom/client'
import { ErrorBoundary } from "react-error-boundary";
// REMOVED: @github/spark/spark — Spark-specific runtime, not available outside GitHub Spark

import App from './App.tsx'
import { ErrorFallback } from './ErrorFallback.tsx'

import "./main.css"
import "./styles/theme.css"
import "./index.css"

createRoot(document.getElementById('root')!).render(
  <ErrorBoundary FallbackComponent={ErrorFallback}>
    <App />
   </ErrorBoundary>
)
