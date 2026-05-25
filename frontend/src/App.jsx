import { useState } from 'react'
import LandingPage from './components/LandingPage' // Ajustează calea dacă fișierele nu sunt în folderul 'components'
import ChatPage from './components/ChatPage'

function App() {
  const [page, setPage] = useState('landing')

  return (
    <div>
      {page === 'landing' ? (
        <LandingPage onNavigate={() => setPage('chat')} />
      ) : (
        <ChatPage onBackToLanding={() => setPage('landing')} />
      )}
    </div>
  )
}

export default App