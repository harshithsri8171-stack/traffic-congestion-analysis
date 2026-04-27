import { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { Activity, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError]       = useState('')
  const [loading, setLoading]   = useState(false)

  const { login } = useAuthStore()
  const navigate  = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      toast.success('Welcome back!')
      navigate('/')
    } catch (err: any) {
      const msg = err.response?.data?.detail || 'Invalid credentials. Please try again.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      {/* Left panel */}
      <div className="auth-left">
        <div
          className="auth-bg-blob"
          style={{ width: 400, height: 400, top: -100, left: -100 }}
        />
        <div
          className="auth-bg-blob"
          style={{ width: 300, height: 300, bottom: -80, right: -80, animationDelay: '2s' }}
        />
        <div className="auth-left-content">
          <div style={{ marginBottom: '2rem' }}>
            <div style={{
              width: 64, height: 64,
              background: 'rgba(255,255,255,0.2)',
              borderRadius: 16,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 1.5rem',
            }}>
              <Activity size={32} color="white" />
            </div>
          </div>
          <h1>TrafficIQ<br />Dashboard</h1>
          <p>
            Real-time traffic congestion analysis powered by computer vision and machine learning.
          </p>
          <div style={{ marginTop: '2.5rem', display: 'flex', gap: '2rem', justifyContent: 'center' }}>
            {[['Roads', 'Monitored'], ['Real-time', 'Analysis'], ['ML-Powered', 'Detection']].map(([top, bottom]) => (
              <div key={top} style={{ textAlign: 'center' }}>
                <div style={{ fontWeight: 700, fontSize: '1.125rem' }}>{top}</div>
                <div style={{ fontSize: '0.75rem', opacity: 0.7 }}>{bottom}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel */}
      <div className="auth-right">
        <div className="auth-form-wrapper">
          <div className="auth-form-header">
            <h2>Sign in</h2>
            <p>Enter your credentials to access the dashboard.</p>
          </div>

          {error && (
            <div className="auth-error">
              <AlertCircle size={16} />
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="username">Username</label>
              <input
                id="username"
                className="form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                required
                autoComplete="username"
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <input
                id="password"
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
                autoComplete="current-password"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary btn-lg btn-full"
              style={{ marginTop: '0.5rem' }}
            >
              {loading ? (
                <>
                  <span className="spinner spinner-sm" style={{ borderTopColor: 'white' }} />
                  Signing in...
                </>
              ) : 'Sign in'}
            </button>
          </form>

          <p className="auth-link">
            Don't have an account? <Link to="/register">Create one</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
