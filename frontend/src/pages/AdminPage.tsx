import { useState, useRef, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Road, User } from '@/types'
import Modal from '@/components/Modal'
import toast from 'react-hot-toast'
import { Plus, Edit2, Trash2, UserCheck, UserX, Database, RefreshCw, Upload, Film, CheckCircle } from 'lucide-react'

type Tab = 'roads' | 'users' | 'video'

const ROAD_TYPES = ['highway', 'arterial', 'local', 'expressway', 'ring-road']

const emptyRoadForm = {
  name: '', road_code: '', start_point: '', end_point: '',
  latitude: '', longitude: '', length_km: '', lanes: '2',
  road_type: 'arterial', area_sqm: '', description: '',
}

export default function AdminPage() {
  const qc                              = useQueryClient()
  const [tab, setTab]                   = useState<Tab>('roads')
  const [videoRoadId, setVideoRoadId]   = useState('')
  const [videoFile, setVideoFile]       = useState<File | null>(null)
  const [videoResult, setVideoResult]   = useState<any>(null)
  const fileInputRef                    = useRef<HTMLInputElement>(null)
  const [addOpen, setAddOpen]           = useState(false)
  const [addFromVideo, setAddFromVideo] = useState(false)
  const [editRoad, setEditRoad]         = useState<Road | null>(null)
  const [deleteRoad, setDeleteRoad]     = useState<Road | null>(null)
  const [form, setForm]                 = useState(emptyRoadForm)
  const [roadSearch, setRoadSearch]     = useState('')
  const [roadComboOpen, setRoadComboOpen] = useState(false)
  const roadComboRef = useRef<HTMLDivElement>(null)

  const setF = (k: keyof typeof emptyRoadForm) => (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => setForm((p) => ({ ...p, [k]: e.target.value }))

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (roadComboRef.current && !roadComboRef.current.contains(e.target as Node)) {
        setRoadComboOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  /* ── Queries ── */
  const { data: roads = [], isLoading: roadsLoading } = useQuery({
    queryKey: ['admin-roads'],
    queryFn: () => api.listRoads(false),
  })

  const { data: users = [], isLoading: usersLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.listUsers(),
  })

  /* ── Mutations ── */
  const addMut = useMutation({
    mutationFn: (data: any) => api.addRoad(data),
    onSuccess: (newRoad: any) => {
      qc.invalidateQueries({ queryKey: ['admin-roads'] })
      qc.invalidateQueries({ queryKey: ['admin-roads-public'] })
      toast.success('Road added successfully!')
      if (addFromVideo) {
        setVideoRoadId(String(newRoad.id))
        setVideoResult(null)
        setTab('video')
      }
      setAddOpen(false)
      setAddFromVideo(false)
      setForm(emptyRoadForm)
    },
    onError: (e: any) => toast.error(e.response?.data?.detail ?? 'Failed to add road'),
  })

  const updateMut = useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => api.updateRoad(id, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-roads'] })
      qc.invalidateQueries({ queryKey: ['admin-roads-public'] })
      toast.success('Road updated!')
      setEditRoad(null)
    },
    onError: (e: any) => toast.error(e.response?.data?.detail ?? 'Failed to update road'),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => api.deleteRoad(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin-roads'] })
      qc.invalidateQueries({ queryKey: ['admin-roads-public'] })
      toast.success('Road deleted.')
      setDeleteRoad(null)
    },
    onError: (e: any) => toast.error(e.response?.data?.detail ?? 'Failed to delete road'),
  })

  const toggleMut = useMutation({
    mutationFn: (id: number) => api.toggleUserActive(id),
    onSuccess: (updated: any) => {
      qc.invalidateQueries({ queryKey: ['admin-users'] })
      toast.success(`User ${updated.is_active ? 'activated' : 'deactivated'}.`)
    },
    onError: () => toast.error('Failed to toggle user status'),
  })

  const seedMut = useMutation({
    mutationFn: () => api.seedData(),
    onSuccess: () => {
      qc.invalidateQueries()
      toast.success('Demo data seeded! Dashboard is now populated.')
    },
    onError: (e: any) => toast.error(e.response?.data?.detail ?? 'Seed failed'),
  })

  const videoMut = useMutation({
    mutationFn: ({ file, roadId }: { file: File; roadId: number }) =>
      api.uploadVideo(file, roadId),
    onSuccess: (data: any) => {
      qc.invalidateQueries()
      setVideoResult(data)
      setVideoFile(null)
      setVideoRoadId('')
      if (fileInputRef.current) fileInputRef.current.value = ''
      toast.success(`Video processed! ${data.vehicle_count} vehicles detected.`)
    },
    onError: (e: any) => toast.error(e.response?.data?.detail ?? 'Video processing failed'),
  })

  /* ── Helpers ── */
  const buildPayload = (f: typeof emptyRoadForm) => ({
    name:        f.name,
    road_code:   f.road_code,
    start_point: f.start_point || undefined,
    end_point:   f.end_point   || undefined,
    latitude:    f.latitude    ? Number(f.latitude)  : undefined,
    longitude:   f.longitude   ? Number(f.longitude) : undefined,
    length_km:   f.length_km   ? Number(f.length_km) : undefined,
    lanes:       f.lanes       ? Number(f.lanes)     : 2,
    road_type:   f.road_type   || undefined,
    area_sqm:    f.area_sqm    ? Number(f.area_sqm)  : undefined,
    description: f.description || undefined,
  })

  const openEdit = (road: Road) => {
    setForm({
      name:        road.name,
      road_code:   road.road_code,
      start_point: road.start_point ?? '',
      end_point:   road.end_point   ?? '',
      latitude:    road.latitude    ? String(road.latitude)  : '',
      longitude:   road.longitude   ? String(road.longitude) : '',
      length_km:   road.length_km   ? String(road.length_km) : '',
      lanes:       String(road.lanes ?? 2),
      road_type:   road.road_type   ?? 'arterial',
      area_sqm:    road.area_sqm    ? String(road.area_sqm)  : '',
      description: road.description ?? '',
    })
    setEditRoad(road)
  }

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    addMut.mutate(buildPayload(form))
  }

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editRoad) return
    updateMut.mutate({ id: editRoad.id, data: buildPayload(form) })
  }

  /* ── Road Form JSX ── */
  const RoadForm = (
    <form id="road-form" onSubmit={editRoad ? handleEditSubmit : handleAddSubmit}>
      <div className="form-grid">
        <div className="form-group">
          <label className="form-label">Road Name *</label>
          <input className="form-input" value={form.name} onChange={setF('name')}
            placeholder="e.g. MG Road" required />
        </div>
        <div className="form-group">
          <label className="form-label">Road Code *</label>
          <input className="form-input" value={form.road_code} onChange={setF('road_code')}
            placeholder="e.g. MG-001" required />
        </div>
        <div className="form-group">
          <label className="form-label">Start Point</label>
          <input className="form-input" value={form.start_point} onChange={setF('start_point')}
            placeholder="e.g. Brigade Road Junction" />
        </div>
        <div className="form-group">
          <label className="form-label">End Point</label>
          <input className="form-input" value={form.end_point} onChange={setF('end_point')}
            placeholder="e.g. Trinity Circle" />
        </div>
        <div className="form-group">
          <label className="form-label">Latitude</label>
          <input className="form-input" type="number" step="any" value={form.latitude}
            onChange={setF('latitude')} placeholder="e.g. 12.9716" />
        </div>
        <div className="form-group">
          <label className="form-label">Longitude</label>
          <input className="form-input" type="number" step="any" value={form.longitude}
            onChange={setF('longitude')} placeholder="e.g. 77.5946" />
        </div>
        <div className="form-group">
          <label className="form-label">Length (km)</label>
          <input className="form-input" type="number" step="any" value={form.length_km}
            onChange={setF('length_km')} placeholder="e.g. 3.2" />
        </div>
        <div className="form-group">
          <label className="form-label">Lanes</label>
          <input className="form-input" type="number" value={form.lanes}
            onChange={setF('lanes')} min="1" max="12" />
        </div>
        <div className="form-group">
          <label className="form-label">Road Type</label>
          <select className="form-select" value={form.road_type} onChange={setF('road_type')}>
            {ROAD_TYPES.map((t) => (
              <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label className="form-label">Area (m²)</label>
          <input className="form-input" type="number" step="any" value={form.area_sqm}
            onChange={setF('area_sqm')} placeholder="e.g. 4800" />
        </div>
        <div className="form-group full">
          <label className="form-label">Description</label>
          <textarea className="form-textarea" value={form.description}
            onChange={setF('description') as any}
            placeholder="Optional description..." />
        </div>
      </div>
    </form>
  )

  return (
    <div>
      <div className="page-header">
        <h1>Admin Panel</h1>
        <p>Manage roads, users, and seed demo data.</p>
      </div>

      {/* Seed banner */}
      <div style={{
        background: 'linear-gradient(135deg, #1e293b 0%, #1d4ed8 100%)',
        borderRadius: 'var(--radius-md)', padding: '1.25rem 1.5rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: '1.75rem', flexWrap: 'wrap', gap: '1rem',
      }}>
        <div>
          <div style={{ color: 'white', fontWeight: 600, marginBottom: 4 }}>Seed Demo Data</div>
          <div style={{ color: '#94a3b8', fontSize: '0.875rem' }}>
            Populate the database with sample roads and traffic records for testing.
          </div>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => seedMut.mutate()}
          disabled={seedMut.isPending}
        >
          {seedMut.isPending
            ? <><span className="spinner spinner-sm" style={{ borderTopColor: 'white' }} />Seeding...</>
            : <><Database size={15} />Seed Demo Data</>}
        </button>
      </div>

      {/* Tabs */}
      <div className="admin-tabs">
        <button className={`admin-tab ${tab === 'roads' ? 'active' : ''}`} onClick={() => setTab('roads')}>
          Roads ({roads.length})
        </button>
        <button className={`admin-tab ${tab === 'users' ? 'active' : ''}`} onClick={() => setTab('users')}>
          Users ({users.length})
        </button>
        <button className={`admin-tab ${tab === 'video' ? 'active' : ''}`} onClick={() => setTab('video')}>
          Video Analysis
        </button>
      </div>

      {/* ── Roads Tab ── */}
      {tab === 'roads' && (
        <div>
          <div className="admin-toolbar">
            <h2>Road Segments</h2>
            <button className="btn btn-primary btn-sm" onClick={() => { setForm(emptyRoadForm); setAddOpen(true) }}>
              <Plus size={15} />Add Road
            </button>
          </div>

          {roadsLoading ? (
            <div className="loading-page" style={{ minHeight: 200 }}>
              <div className="spinner" />
            </div>
          ) : roads.length === 0 ? (
            <div className="empty-state">
              <h3>No roads yet</h3>
              <p>Add a road or seed demo data to get started.</p>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Code</th>
                    <th>Type</th>
                    <th>Lanes</th>
                    <th>Length</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {roads.map((road: Road) => (
                    <tr key={road.id}>
                      <td className="td-muted">{road.id}</td>
                      <td style={{ fontWeight: 500 }}>{road.name}</td>
                      <td><span className="badge badge-gray">{road.road_code}</span></td>
                      <td className="td-muted">{road.road_type ?? 'N/A'}</td>
                      <td className="td-muted">{road.lanes}</td>
                      <td className="td-muted">{road.length_km ? `${road.length_km} km` : '—'}</td>
                      <td>
                        <span className={`badge ${road.is_active ? 'badge-success' : 'badge-gray'}`}>
                          {road.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.375rem' }}>
                          <button className="btn btn-secondary btn-sm btn-icon" title="Edit"
                            onClick={() => openEdit(road)}>
                            <Edit2 size={13} />
                          </button>
                          <button className="btn btn-danger btn-sm btn-icon" title="Delete"
                            onClick={() => setDeleteRoad(road)}>
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Users Tab ── */}
      {tab === 'users' && (
        <div>
          <div className="admin-toolbar">
            <h2>User Accounts</h2>
            <button className="btn btn-secondary btn-sm" onClick={() => qc.invalidateQueries({ queryKey: ['admin-users'] })}>
              <RefreshCw size={14} />Refresh
            </button>
          </div>

          {usersLoading ? (
            <div className="loading-page" style={{ minHeight: 200 }}>
              <div className="spinner" />
            </div>
          ) : users.length === 0 ? (
            <div className="empty-state">
              <h3>No users found</h3>
            </div>
          ) : (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Username</th>
                    <th>Full Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user: User) => (
                    <tr key={user.id}>
                      <td className="td-muted">{user.id}</td>
                      <td style={{ fontWeight: 500 }}>{user.username}</td>
                      <td className="td-muted">{user.full_name ?? '—'}</td>
                      <td className="td-muted">{user.email}</td>
                      <td>
                        <span className={`badge ${
                          user.role === 'admin' ? 'badge-danger' :
                          user.role === 'authority' ? 'badge-primary' : 'badge-gray'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${user.is_active ? 'badge-success' : 'badge-gray'}`}>
                          {user.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td>
                        <button
                          className={`btn btn-sm ${user.is_active ? 'btn-secondary' : 'btn-success'}`}
                          onClick={() => toggleMut.mutate(user.id)}
                          disabled={toggleMut.isPending}
                          title={user.is_active ? 'Deactivate' : 'Activate'}
                        >
                          {user.is_active
                            ? <><UserX size={13} />Deactivate</>
                            : <><UserCheck size={13} />Activate</>}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Video Analysis Tab ── */}
      {tab === 'video' && (
        <div>
          <div className="admin-toolbar">
            <h2>Video Analysis</h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            {/* Upload form */}
            <div className="card">
              <div className="card-header">
                <h3>Upload CCTV Footage</h3>
              </div>
              <div className="card-body" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  Upload a video file and the system will run YOLOv8 vehicle detection,
                  classify congestion, and save a traffic record automatically.
                </p>

                <div className="form-group" ref={roadComboRef}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.375rem' }}>
                    <label className="form-label" style={{ margin: 0 }}>Select Road *</label>
                    <button
                      className="btn btn-ghost btn-sm"
                      style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}
                      onClick={() => { setAddFromVideo(true); setForm(emptyRoadForm); setAddOpen(true) }}
                    >
                      <Plus size={13} /> Add new road
                    </button>
                  </div>

                  {/* Single combobox input */}
                  <div style={{ position: 'relative' }}>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="Type to search roads…"
                      value={
                        videoRoadId && roadSearch === ''
                          ? `${roads.find((r: Road) => String(r.id) === videoRoadId)?.name ?? ''} (${roads.find((r: Road) => String(r.id) === videoRoadId)?.road_code ?? ''})`
                          : roadSearch
                      }
                      onFocus={() => { setRoadSearch(''); setRoadComboOpen(true) }}
                      onChange={e => {
                        setRoadSearch(e.target.value)
                        setVideoRoadId('')
                        setVideoResult(null)
                        setRoadComboOpen(true)
                      }}
                      style={{ paddingRight: '2rem' }}
                    />
                    <span
                      style={{
                        position: 'absolute', right: '0.625rem', top: '50%',
                        transform: 'translateY(-50%)', color: 'var(--text-secondary)',
                        cursor: 'pointer', fontSize: '0.75rem', userSelect: 'none',
                      }}
                      onClick={() => {
                        if (videoRoadId) { setVideoRoadId(''); setRoadSearch(''); setVideoResult(null); setRoadComboOpen(true) }
                        else setRoadComboOpen(o => !o)
                      }}
                    >
                      {videoRoadId ? '✕' : '▾'}
                    </span>
                  </div>

                  {/* Inline dropdown — pushes content down, no overlap */}
                  {roadComboOpen && (
                    <div style={{
                      marginTop: '4px',
                      border: '1px solid var(--border)',
                      borderRadius: 'var(--radius)',
                      overflow: 'hidden',
                      maxHeight: '200px',
                      overflowY: 'auto',
                      boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
                    }}>
                      {(() => {
                        const filtered = roads.filter((r: Road) =>
                          !roadSearch ||
                          r.name.toLowerCase().includes(roadSearch.toLowerCase()) ||
                          r.road_code.toLowerCase().includes(roadSearch.toLowerCase())
                        )
                        if (filtered.length === 0) return (
                          <div style={{ padding: '0.75rem 1rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                            No roads match "{roadSearch}".{' '}
                            <span
                              style={{ color: 'var(--primary)', cursor: 'pointer', fontWeight: 500 }}
                              onMouseDown={() => { setAddFromVideo(true); setForm({ ...emptyRoadForm, name: roadSearch }); setAddOpen(true); setRoadComboOpen(false) }}
                            >
                              + Create it
                            </span>
                          </div>
                        )
                        return filtered.map((r: Road, i: number) => (
                          <div
                            key={r.id}
                            onMouseDown={() => {
                              setVideoRoadId(String(r.id))
                              setRoadSearch('')
                              setVideoResult(null)
                              setRoadComboOpen(false)
                            }}
                            style={{
                              padding: '0.6rem 0.875rem',
                              cursor: 'pointer',
                              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                              background: String(r.id) === videoRoadId ? '#eff6ff' : i % 2 === 0 ? '#fff' : '#f8fafc',
                              borderBottom: i < filtered.length - 1 ? '1px solid var(--border)' : 'none',
                              transition: 'background 0.1s',
                            }}
                            onMouseEnter={e => (e.currentTarget.style.background = '#dbeafe')}
                            onMouseLeave={e => (e.currentTarget.style.background =
                              String(r.id) === videoRoadId ? '#eff6ff' : i % 2 === 0 ? '#fff' : '#f8fafc')}
                          >
                            <span style={{ fontWeight: 500, fontSize: '0.875rem' }}>{r.name}</span>
                            <span style={{
                              fontSize: '0.7rem', fontWeight: 600, letterSpacing: '0.03em',
                              color: '#3b82f6', background: '#eff6ff',
                              padding: '2px 6px', borderRadius: '4px',
                            }}>{r.road_code}</span>
                          </div>
                        ))
                      })()}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Video File *</label>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/mp4,video/avi,video/quicktime,video/x-matroska,video/webm"
                    className="form-input"
                    style={{ padding: '0.5rem' }}
                    onChange={e => { setVideoFile(e.target.files?.[0] ?? null); setVideoResult(null) }}
                  />
                  <span className="form-hint">Supported: MP4, AVI, MOV, MKV, WebM</span>
                </div>

                {videoFile && (
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: '0.625rem',
                    padding: '0.75rem', background: 'var(--gray-50)',
                    borderRadius: 'var(--radius)', border: '1px solid var(--border)',
                    fontSize: '0.875rem',
                  }}>
                    <Film size={16} color="var(--primary)" />
                    <div>
                      <div style={{ fontWeight: 500 }}>{videoFile.name}</div>
                      <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
                        {(videoFile.size / (1024 * 1024)).toFixed(1)} MB
                      </div>
                    </div>
                  </div>
                )}

                <button
                  className="btn btn-primary"
                  disabled={!videoFile || !videoRoadId || videoMut.isPending}
                  onClick={() => videoMut.mutate({ file: videoFile!, roadId: Number(videoRoadId) })}
                >
                  {videoMut.isPending ? (
                    <><span className="spinner spinner-sm" style={{ borderTopColor: 'white' }} />Processing video...</>
                  ) : (
                    <><Upload size={15} />Run Analysis</>
                  )}
                </button>

                {videoMut.isPending && (
                  <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                    YOLOv8 is processing frames... this may take a moment.
                  </p>
                )}
              </div>
            </div>

            {/* Result panel */}
            <div className="card">
              <div className="card-header">
                <h3>Analysis Result</h3>
              </div>
              <div className="card-body">
                {!videoResult ? (
                  <div className="empty-state">
                    <Film size={36} />
                    <h3>No result yet</h3>
                    <p>Upload a video to see detection results here.</p>
                  </div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.625rem' }}>
                      <CheckCircle size={20} color="var(--success)" />
                      <span style={{ fontWeight: 600, color: 'var(--success)' }}>
                        Processing complete
                      </span>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                      {[
                        ['Road', videoResult.road_name],
                        ['Frames Analysed', videoResult.frames_processed],
                        ['Unique Vehicles (total passed)', videoResult.vehicle_count],
                        ['Peak Concurrent', videoResult.peak_concurrent ?? '—'],
                        ['Est. Speed', `${videoResult.average_speed?.toFixed(1)} km/h`],
                        ['Congestion Score', `${videoResult.congestion_score?.toFixed(1)} / 100`],
                        ['Level', videoResult.congestion_level?.replace('_', ' ').toUpperCase()],
                      ].map(([label, value]) => (
                        <div key={label as string} style={{
                          padding: '0.75rem', background: 'var(--gray-50)',
                          borderRadius: 'var(--radius)', border: '1px solid var(--border)',
                        }}>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: 2 }}>{label}</div>
                          <div style={{ fontWeight: 700, fontSize: '1rem' }}>{value}</div>
                        </div>
                      ))}
                    </div>

                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>
                      A traffic record has been saved and the dashboard will reflect the new data.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── Add Road Modal ── */}
      <Modal
        isOpen={addOpen}
        onClose={() => setAddOpen(false)}
        title="Add New Road"
        size="lg"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setAddOpen(false)}>Cancel</button>
            <button className="btn btn-primary" form="road-form" type="submit" disabled={addMut.isPending}>
              {addMut.isPending
                ? <><span className="spinner spinner-sm" style={{ borderTopColor: 'white' }} />Saving...</>
                : 'Add Road'}
            </button>
          </>
        }
      >
        {RoadForm}
      </Modal>

      {/* ── Edit Road Modal ── */}
      <Modal
        isOpen={!!editRoad}
        onClose={() => setEditRoad(null)}
        title={`Edit Road — ${editRoad?.name ?? ''}`}
        size="lg"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setEditRoad(null)}>Cancel</button>
            <button className="btn btn-primary" form="road-form" type="submit" disabled={updateMut.isPending}>
              {updateMut.isPending
                ? <><span className="spinner spinner-sm" style={{ borderTopColor: 'white' }} />Saving...</>
                : 'Save Changes'}
            </button>
          </>
        }
      >
        {RoadForm}
      </Modal>

      {/* ── Delete Confirm Modal ── */}
      <Modal
        isOpen={!!deleteRoad}
        onClose={() => setDeleteRoad(null)}
        title="Delete Road"
        size="sm"
        footer={
          <>
            <button className="btn btn-secondary" onClick={() => setDeleteRoad(null)}>Cancel</button>
            <button
              className="btn btn-danger"
              onClick={() => deleteRoad && deleteMut.mutate(deleteRoad.id)}
              disabled={deleteMut.isPending}
            >
              {deleteMut.isPending
                ? <><span className="spinner spinner-sm" style={{ borderTopColor: 'white' }} />Deleting...</>
                : 'Delete'}
            </button>
          </>
        }
      >
        <div className="confirm-icon"><Trash2 size={22} /></div>
        <div className="confirm-text">
          <h3>Delete "{deleteRoad?.name}"?</h3>
          <p>This will permanently delete the road and all its traffic records. This action cannot be undone.</p>
        </div>
      </Modal>
    </div>
  )
}
