import './App.css'
import { useEffect , useState } from 'react'

function App() {
  
  const [msg , setMsg] = useState('Loading...');

  useEffect(()=>{
    async function load() {
      const res = await fetch("http://127.0.0.1:8000");
      const data = await res.json()
      setMsg(data.message)
      console.log(data)
    }
    load();
  },[])

  return (
    <h1>{msg}</h1>
    
  )
}

export default App
