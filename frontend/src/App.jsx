import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [items, setItems] = useState([])
  const [auditLogs, setAuditLogs] = useState([])
  const [status, setStatus] = useState("Loading...")
  const [newName, setNewName] = useState("")
  const [newDescription, setNewDescription] = useState("")
  const [persona, setPersona] = useState("Admin")

  const GATEWAY_URL = 'http://localhost:8080'

  const getHeaders = () => {
    return {
      'X-Persona': persona,
      'Content-Type': 'application/json'
    }
  }

  const fetchItems = () => {
    fetch(`${GATEWAY_URL}/api/items`, { headers: getHeaders() })
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(err => console.error("Error fetching items:", err));
  }

  const fetchAuditLogs = () => {
    fetch(`${GATEWAY_URL}/api/audit`, { headers: getHeaders() })
      .then(res => res.json())
      .then(data => setAuditLogs(data))
      .catch(err => console.error("Error fetching audit logs:", err));
  }

  useEffect(() => {
    // Check backend status via gateway
    fetch(`${GATEWAY_URL}/`, { headers: getHeaders() })
      .then(res => res.json())
      .then(data => setStatus(data.message))
      .catch(err => setStatus("Error connecting to gateway"));

    fetchItems();
    fetchAuditLogs();
  }, [persona]) // Refetch when persona changes to test permissions

  const handleCreate = (e) => {
    e.preventDefault();
    if (!newName.trim() || !newDescription.trim()) return;

    fetch(`${GATEWAY_URL}/api/items?name=${encodeURIComponent(newName)}&description=${encodeURIComponent(newDescription)}`, {
      method: 'POST',
      headers: getHeaders()
    })
      .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        return res.json();
      })
      .then(() => {
        setNewName("");
        setNewDescription("");
        fetchItems();
        fetchAuditLogs();
      })
      .catch(err => alert("Error creating item: " + err.message));
  };

  const handleToggleStatus = (id, currentStatus) => {
    fetch(`${GATEWAY_URL}/api/items/${id}?completed=${!currentStatus}`, {
      method: 'PUT',
      headers: getHeaders()
    })
      .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        fetchItems();
        fetchAuditLogs();
      })
      .catch(err => alert("Error updating item: " + err.message));
  };

  const handleDelete = (id) => {
    fetch(`${GATEWAY_URL}/api/items/${id}`, {
      method: 'DELETE',
      headers: getHeaders()
    })
      .then(res => {
        if (!res.ok) throw new Error("Unauthorized");
        fetchItems();
        fetchAuditLogs();
      })
      .catch(err => alert("Error deleting item: " + err.message));
  };

  return (
    <>
      <div className="persona-selector" style={{ position: 'fixed', top: 10, right: 10, background: '#fff', padding: 10, borderRadius: 5, color: '#000' }}>
        <label style={{ marginRight: 10 }}>Persona:</label>
        <select value={persona} onChange={(e) => setPersona(e.target.value)}>
          <option value="Admin">Admin</option>
          <option value="User">User</option>
          <option value="Viewer">Viewer</option>
        </select>
      </div>

      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Macroservices & Microservices</h1>
      
      <div className="card">
        <h3>Gateway Status: {status}</h3>
      </div>

      {persona !== 'Viewer' && (
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
      )}

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
                  {persona !== 'Viewer' && (
                    <button onClick={() => handleToggleStatus(item.id, item.completed)}>
                      {item.completed ? 'Undo' : 'Complete'}
                    </button>
                  )}
                  {persona === 'Admin' && (
                    <button className="delete-btn" onClick={() => handleDelete(item.id)}>Delete</button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <h3>Audit Logs (from Audit Service):</h3>
        {auditLogs.length === 0 ? (
          <p>No logs found.</p>
        ) : (
          <ul className="item-list" style={{ textAlign: 'left', fontSize: '0.9em' }}>
            {auditLogs.map(log => (
              <li key={log.id} style={{ marginBottom: 5 }}>
                [{new Date(log.created_at).toLocaleString()}] {log.action} on table {log.table_name} (Record ID: {log.record_id})
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  )
}

export default App
