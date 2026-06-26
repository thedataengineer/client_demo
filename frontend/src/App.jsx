import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [items, setItems] = useState([])
  const [status, setStatus] = useState("Loading...")
  const [newName, setNewName] = useState("")
  const [newDescription, setNewDescription] = useState("")

  const fetchItems = () => {
    fetch('http://localhost:8000/api/items')
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(err => console.error("Error fetching items:", err));
  }

  useEffect(() => {
    // Check backend status
    fetch('http://localhost:8000/')
      .then(res => res.json())
      .then(data => setStatus(data.message))
      .catch(err => setStatus("Error connecting to backend"));

    // Fetch items
    fetchItems();
  }, [])

  const handleCreate = (e) => {
    e.preventDefault();
    if (!newName.trim() || !newDescription.trim()) return;

    fetch(`http://localhost:8000/api/items?name=${encodeURIComponent(newName)}&description=${encodeURIComponent(newDescription)}`, {
      method: 'POST'
    })
      .then(res => res.json())
      .then(() => {
        setNewName("");
        setNewDescription("");
        fetchItems();
      })
      .catch(err => console.error("Error creating item:", err));
  };

  const handleToggleStatus = (id, currentStatus) => {
    fetch(`http://localhost:8000/api/items/${id}?completed=${!currentStatus}`, {
      method: 'PUT'
    })
      .then(() => fetchItems())
      .catch(err => console.error("Error updating item:", err));
  };

  const handleDelete = (id) => {
    fetch(`http://localhost:8000/api/items/${id}`, {
      method: 'DELETE'
    })
      .then(() => fetchItems())
      .catch(err => console.error("Error deleting item:", err));
  };

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
        <h3>Add New Item</h3>
        <form onSubmit={handleCreate} className="add-form">
          <input 
            type="text" 
            placeholder="Name" 
            value={newName} 
            onChange={(e) => setNewName(e.target.value)} 
          />
          <input 
            type="text" 
            placeholder="Description" 
            value={newDescription} 
            onChange={(e) => setNewDescription(e.target.value)} 
          />
          <button type="submit">Add</button>
        </form>
      </div>

      <div className="card">
        <h3>Items from Database:</h3>
        {items.length === 0 ? (
          <p>No items found.</p>
        ) : (
          <ul className="item-list">
            {items.map(item => (
              <li key={item.id} className={`item ${item.completed ? 'completed' : ''}`}>
                <div className="item-content">
                  <strong>{item.name}</strong>: {item.description}
                </div>
                <div className="item-actions">
                  <button onClick={() => handleToggleStatus(item.id, item.completed)}>
                    {item.completed ? 'Undo' : 'Complete'}
                  </button>
                  <button className="delete-btn" onClick={() => handleDelete(item.id)}>Delete</button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  )
}

export default App
