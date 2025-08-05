import React from 'react'
import { AuthProvider } from './contexts/AuthContext'
import FeedNew from './Components/Feed'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Feed/>
      </div>
    </AuthProvider>
  )
}

export default App
