import { useState } from 'react'
import LandingPage from './components/LandingPage'

function App() {
  const [hasStarted, setHasStarted] = useState(false)

  const handleStart = () => {
    if (!hasStarted) {
      setHasStarted(true)
    }
  }

  return (
    <div onKeyDown={handleStart} tabIndex={0} style={{ outline: 'none' }}>
      {!hasStarted ? (
        <LandingPage />
      ) : (
        <div className="w-full min-h-screen flex items-center justify-center bg-gradient-to-br from-pink-200 to-pink-100">
          <p className="text-2xl text-gray-600">Aplicație în dezvoltare...</p>
        </div>
      )}
    </div>
  )
}

export default App
