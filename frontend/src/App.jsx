import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [items, setItems] = useState([])
  const [status, setStatus] = useState("Loading...")

  useEffect(() => {
    // Check backend status
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setStatus(data.message))
      .catch(err => setStatus("Error connecting to backend"));

    // Fetch items
    fetch('http://localhost:8000/api/items')
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(err => console.error("Error fetching items:", err));
  }, [])

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      
      <div className="card">
        <h3>Backend Status: {status}</h3>
      </div>

      <div className="card">
        <h3>Items from Database:</h3>
        {items.length === 0 ? (
          <p>No items found.</p>
        ) : (
          <ul>
            {items.map(item => (
              <li key={item.id}>
                <strong>{item.name}</strong>: {item.description}
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  )
}

export default App
