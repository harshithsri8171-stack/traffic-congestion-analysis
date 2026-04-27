import { useState, FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { api } from '@/services/api'
import { Activity, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: '', email: '', full_name: '', password: '', confirm: '',
  })
  const [error, setError]     = useState('')
  const [loading, setLoading] = useState(false)
  const navigate              = useNavigate()

  const set = (k: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [k]: e.target.value }))

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) { setError('Passwords do not match.'); return }
    if (form.password.length < 8) { setError('Password must be at least 8 characters.'); return }
    setLoading(true)
    try {
      await api.register({
        username: form.username,
        email: form.email,
        full_name: form.full_name,
        password: form.password,
      })
      toast.success('Account created! Please sign in.')
      navigate('/login')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed. Try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-left">
        <div className="auth-bg-blob" style={{ width: 350, height: 350, top: -80, right: -80 }} />
        <div className="auth-bg-blob" style={{ width: 250, height: 250, bottom: -60, left: -60, animationDelay: '3s' }} />
        <div className="auth-left-content">
          <div style={{ width:64, height:64, background:'rgba(255,255,255,0.2)', borderRadius:16,
            display:'flex', alignItems:'center', justifyContent:'center', margin:'0 auto 1.5rem' }}>
            <Activity size={32} color="white" />
          </div>
          <h1>Join TrafficIQ</h1>
          <p>Monitor city-wide traffic congestion in real time with ML-powered insights and beautiful visualisations.</p>
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-form-wrapper">
          <div className="auth-form-header">
            <h2>Create account</h2>
            <p>Fill in the form below to get started.</p>
          </div>

          {error && (
            <div className="auth-error">
              <AlertCircle size={16} />{error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display:'flex', flexDirection:'column', gap:'1rem' }}>
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input className="form-input" type="text" value={form.full_name} onChange={set('full_name')}
                placeholder="Your full name" autoFocus />
            </div>
            <div className="form-group">
              <label className="form-label">Username *</label>
              <input className="form-input" type="text" value={form.username} onChange={set('username')}
                placeholder="Choose a username" required />
            </div>
            <div className="form-group">
              <label className="form-label">Email *</label>
              <input className="form-input" type="email" value={form.email} onChange={set('email')}
                placeholder="you@example.com" required />
            </div>
            <div className="form-group">
              <label className="form-label">Password *</label>
              <input className="form-input" type="password" value={form.password} onChange={set('password')}
                placeholder="Min. 8 characters" required />
            </div>
            <div className="form-group">
              <label className="form-label">Confirm Password *</label>
              <input className="form-input" type="password" value={form.confirm} onChange={set('confirm')}
                placeholder="Repeat password" required />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary btn-lg btn-full" style={{ marginTop:'0.25rem' }}>
              {loading ? (<><span className="spinner spinner-sm" style={{ borderTopColor:'white' }} />Creating account...</>) : 'Create account'}
            </button>
          </form>

          <p className="auth-link">Already have an account? <Link to="/login">Sign in</Link></p>
        </div>
      </div>
    </div>
  )
}
