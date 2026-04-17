import React, { useState } from 'react';
import { motion as Motion, AnimatePresence } from 'framer-motion';
import { Send, LogOut, Calendar, Users, MapPin, DollarSign, Search, Loader2 } from 'lucide-react';

const API_BASE_URL = '/api/v1';

function App() {
  const [user, setUser] = useState(() => {
    const savedToken = localStorage.getItem('token');
    return savedToken ? { email: 'user@example.com' } : null;
  });
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [eventContext, setEventContext] = useState({
    event_type: '',
    event_category: '',
    event_topic: '',
    location: '',
    expected_footfall: 100,
    max_budget: 10000,
    target_audience: '',
    search_domains: 'google.com, linkedin.com, twitter.com'
  });

  const [reports, setReports] = useState([]);
  const [planning, setPlanning] = useState(false);


  const handleAuth = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const endpoint = isLogin ? '/auth/login' : '/auth/register';
    const formData = new URLSearchParams();
    
    if (isLogin) {
      formData.append('username', email);
      formData.append('password', password);
    }

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: isLogin ? { 'Content-Type': 'application/x-www-form-urlencoded' } : { 'Content-Type': 'application/json' },
        body: isLogin ? formData : JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.detail || 'Authentication failed');

      const accessToken = data.access_token || data.token;
      setToken(accessToken);
      localStorage.setItem('token', accessToken);
      setUser({ email });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
  };

  const startPlanning = async (e) => {
    e.preventDefault();
    setPlanning(true);
    setReports([]);
    setError('');

    try {
      // 1. Create a session first
      const sessionResponse = await fetch(`${API_BASE_URL}/auth/session`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const sessionData = await sessionResponse.json();
      if (!sessionResponse.ok) throw new Error(sessionData.detail || 'Failed to create session');
      
      const sessionToken = sessionData.token.access_token;

      // 2. Start streaming from /event/plan
      const url = `${API_BASE_URL}/event/plan`;
      
      // Use Fetch API for streaming since EventSource doesn't support custom headers easily
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${sessionToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(eventContext)
      });

      if (!response.ok) throw new Error('Failed to start planning');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data === '[DONE]') {
                setPlanning(false);
                break;
              }
              if (typeof data === 'string' && data.startsWith('ERROR: ')) {
                setError(data);
                setPlanning(false);
                break;
              }
              setReports(prev => [...prev, data]);
            } catch (e) {
              console.error('Error parsing SSE data', e);
            }
          }
        }
      }
    } catch (err) {
      setError(err.message);
      setPlanning(false);
    }
  };

  if (!user) {
    return (
      <div className="container" style={{ maxWidth: '500px', marginTop: '10vh' }}>
        <Motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 style={{ fontSize: '4rem', marginBottom: '2rem' }}>EVENT<br/>AGENT.</h1>
          <p style={{ color: '#666' }}>Professional AI-driven event orchestration.</p>
          
          <form onSubmit={handleAuth} className="flex-col">
            <input 
              type="email" 
              placeholder="EMAIL" 
              value={email} 
              onChange={e => setEmail(e.target.value)}
              required
            />
            <input 
              type="password" 
              placeholder="PASSWORD" 
              value={password} 
              onChange={e => setPassword(e.target.value)}
              required
            />
            {error && <p style={{ color: 'red', fontSize: '0.8rem' }}>{error}</p>}
            <button type="submit" disabled={loading}>
              {loading ? <Loader2 className="animate-spin" /> : (isLogin ? 'LOGIN' : 'REGISTER')}
            </button>
            <p 
              onClick={() => setIsLogin(!isLogin)} 
              style={{ cursor: 'pointer', textAlign: 'center', marginTop: '1rem', fontWeight: 700, fontSize: '0.9rem' }}
            >
              {isLogin ? 'OR CREATE ACCOUNT' : 'OR LOGIN'}
            </p>
          </form>
        </Motion.div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="flex justify-between items-center" style={{ marginBottom: '10vh' }}>
        <div>
          <h1 style={{ fontSize: '3rem' }}>PLANNER.</h1>
          <p className="tag">AGENTIC SYSTEM V1.0</p>
        </div>
        <button onClick={handleLogout} style={{ padding: '8px 16px', fontSize: '0.8rem' }}>
          <LogOut size={16} />
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '80px' }}>
        <Motion.section
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <h2 style={{ marginBottom: '2rem' }}>CONTEXT.</h2>
          <form onSubmit={startPlanning} className="flex-col">
            <div className="flex-col">
              <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>EVENT TYPE</label>
              <input 
                placeholder="CONFERENCE, FESTIVAL..." 
                value={eventContext.event_type}
                onChange={e => setEventContext({...eventContext, event_type: e.target.value})}
                required
              />
            </div>
            <div className="flex-col">
              <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>CATEGORY</label>
              <input 
                placeholder="AI, MUSIC, SPORTS..." 
                value={eventContext.event_category}
                onChange={e => setEventContext({...eventContext, event_category: e.target.value})}
                required
              />
            </div>
            <div className="flex-col">
              <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>TOPIC</label>
              <input 
                placeholder="MAIN THEME..." 
                value={eventContext.event_topic}
                onChange={e => setEventContext({...eventContext, event_topic: e.target.value})}
                required
              />
            </div>
            <div className="flex-col">
              <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>LOCATION</label>
              <input 
                placeholder="CITY, COUNTRY..." 
                value={eventContext.location}
                onChange={e => setEventContext({...eventContext, location: e.target.value})}
                required
              />
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
              <div className="flex-col">
                <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>FOOTFALL</label>
                <input 
                  type="number"
                  placeholder="100" 
                  value={eventContext.expected_footfall}
                  onChange={e => setEventContext({...eventContext, expected_footfall: parseInt(e.target.value)})}
                  required
                />
              </div>
              <div className="flex-col">
                <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>BUDGET ($)</label>
                <input 
                  type="number"
                  placeholder="10000" 
                  value={eventContext.max_budget}
                  onChange={e => setEventContext({...eventContext, max_budget: parseFloat(e.target.value)})}
                  required
                />
              </div>
            </div>
            <div className="flex-col">
              <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>TARGET AUDIENCE</label>
              <input 
                placeholder="DESCRIPTION OF AUDIENCE..." 
                value={eventContext.target_audience}
                onChange={e => setEventContext({...eventContext, target_audience: e.target.value})}
                required
              />
            </div>
            <div className="flex-col">
              <label style={{ fontWeight: 800, marginBottom: '8px', fontSize: '0.8rem' }}>SEARCH DOMAINS</label>
              <input 
                placeholder="google.com, linkedin.com..." 
                value={eventContext.search_domains}
                onChange={e => setEventContext({...eventContext, search_domains: e.target.value})}
                required
              />
            </div>
            <button type="submit" disabled={planning || loading} style={{ marginTop: '2rem', height: '80px', fontSize: '1.5rem' }}>
              {planning ? <Loader2 className="animate-spin" style={{ margin: '0 auto' }} /> : 'GENERATE PLAN'}
            </button>
          </form>
        </Motion.section>

        <section>
          <h2 style={{ marginBottom: '2rem' }}>OUTPUT.</h2>
          <div style={{ minHeight: '400px', borderLeft: '1px solid #eee', paddingLeft: '40px' }}>
            {reports.length === 0 && !planning && (
              <p style={{ color: '#ccc', fontStyle: 'italic' }}>Awaiting input...</p>
            )}
            <div className="reports-grid">
              <AnimatePresence>
                {reports.map((report, idx) => {
                  const isStructured = typeof report === 'object' && report.agent;
                  return (
                    <Motion.div 
                      key={idx}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="agent-card"
                    >
                      {isStructured ? (
                        <>
                          <div className="agent-header">
                            <span className="agent-name">{report.agent}</span>
                            <span className="status-dot"></span>
                          </div>
                          <div className="agent-body">
                            <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', lineHeight: '1.6' }}>
                              {report.content}
                            </p>
                          </div>
                        </>
                      ) : (
                        <div className="agent-body">
                          <p style={{ whiteSpace: 'pre-wrap', fontSize: '0.9rem', lineHeight: '1.6' }}>
                            {report}
                          </p>
                        </div>
                      )}
                    </Motion.div>
                  );
                })}
              </AnimatePresence>
            </div>
            {planning && (
              <Motion.div 
                animate={{ opacity: [0.4, 1, 0.4] }} 
                transition={{ repeat: Infinity, duration: 1.5 }}
                style={{ fontWeight: 800, fontSize: '0.8rem', letterSpacing: '0.1em' }}
              >
                AGENTS ARE WORKING...
              </Motion.div>
            )}
            {error && <p style={{ color: 'red', fontWeight: 700 }}>{error}</p>}
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
