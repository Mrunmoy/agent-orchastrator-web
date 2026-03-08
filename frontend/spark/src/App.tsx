import { useState } from 'react'
import { MainApp } from '@/components/MainApp'
import { Dashboard } from '@/components/Dashboard'

type View = 'main' | 'dashboard'

function App() {
  const [currentView, setCurrentView] = useState<View>('main')
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)

  const handleNavigateToDashboard = (conversationId: string) => {
    setSelectedConversationId(conversationId)
    setCurrentView('dashboard')
  }

  const handleNavigateBack = () => {
    setCurrentView('main')
    setSelectedConversationId(null)
  }

  if (currentView === 'dashboard' && selectedConversationId) {
    return <Dashboard conversationId={selectedConversationId} onNavigateBack={handleNavigateBack} />
  }

  return <MainApp onNavigateToDashboard={handleNavigateToDashboard} />
}

export default App
