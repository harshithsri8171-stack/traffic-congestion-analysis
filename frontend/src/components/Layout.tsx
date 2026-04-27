import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { UserRole } from '@/types'
import { LayoutDashboard, Map, ShieldCheck, LogOut, Activity } from 'lucide-react'

const PAGE_TITLES: Record<string, string> = {
  '/': 'Dashboard',
  '/heatmap': 'Traffic Heatmap',
  '/admin': 'Admin Panel',
}

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const pageTitle = location.pathname.startsWith('/road/')
    ? 'Road Detail'
    : (PAGE_TITLES[location.pathname] ?? 'Traffic Dashboard')

  const initials = user?.username?.slice(0, 2).toUpperCase() ?? 'U'

  return (
    <div className="app-layout">
      {/* ── Sidebar ── */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <div className="sidebar-logo-icon">
              <Activity size={16} />
            </div>
            <div>
              <div className="sidebar-logo-text">TrafficIQ</div>
              <div className="sidebar-logo-sub">Congestion Analysis</div>
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <span className="sidebar-section-label">Main</span>

          <NavLink
            to="/"
            end
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <LayoutDashboard size={17} />
            Dashboard
          </NavLink>

          <NavLink
            to="/heatmap"
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <Map size={17} />
            Heatmap
          </NavLink>

          {user?.role === UserRole.ADMIN && (
            <>
              <span className="sidebar-section-label">Administration</span>
              <NavLink
                to="/admin"
                className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
              >
                <ShieldCheck size={17} />
                Admin Panel
              </NavLink>
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="sidebar-user">
            <div className="user-avatar">{initials}</div>
            <div className="sidebar-user-info">
              <div className="sidebar-username">{user?.username}</div>
              <div className="sidebar-role">{user?.role}</div>
            </div>
            <button className="logout-btn" onClick={handleLogout} title="Logout">
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <div className="main-wrapper">
        <header className="topbar">
          <span className="topbar-title">{pageTitle}</span>
          <div className="topbar-right">
            <div className="refresh-badge">
              <span className="refresh-dot" />
              Live
            </div>
            <div className="user-badge">
              <div className="user-avatar">{initials}</div>
              {user?.full_name || user?.username}
            </div>
          </div>
        </header>

        <main className="page-content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
