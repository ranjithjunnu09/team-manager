import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate, useParams, useLocation } from "react-router-dom";
import axios from "axios";
import "./index.css";

// ======================================================
// AXIOS INSTANCE
// ======================================================

const API = axios.create({baseURL: import.meta.env.VITE_API_URL});

// ======================================================
// AUTH CONTEXT
// ======================================================

const AuthContext = createContext();
const useAuth = () => useContext(AuthContext);

function AuthProvider({ children }) {
  const [token,   setToken]   = useState(localStorage.getItem("token"));
  const [user,    setUser]    = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        if (token) {
          API.defaults.headers.common["Authorization"] = `Bearer ${token}`;
          const res = await API.get("/me");
          setUser(res.data);
        }
      } catch {
        logout();
      } finally {
        setLoading(false);
      }
    };
    fetchUser();
  }, [token]);

  const login = (accessToken, refreshToken) => {
    localStorage.setItem("token",         accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    setToken(accessToken);
    API.defaults.headers.common["Authorization"] = `Bearer ${accessToken}`;
  };

  const logout = async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    if (refreshToken) {
      await API.post("/logout", { refresh_token: refreshToken }).catch(() => {});
    }
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    setToken(null);
    setUser(null);
    delete API.defaults.headers.common["Authorization"];
  };

  return (
    <AuthContext.Provider value={{ token, user, setUser, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// ======================================================
// PROTECTED ROUTE
// ======================================================

function ProtectedRoute({ children }) {
  const { token, loading } = useAuth();
  if (loading) return <PageLoader />;
  if (!token)  return <Navigate to="/login" />;
  return children;
}

// ======================================================
// DESIGN TOKENS
// ======================================================

const C = {
  bg:          "#F8F9FA",
  surface:     "#FFFFFF",
  border:      "#E2E8F0",
  borderHover: "#CBD5E1",
  accent:      "#2563EB",
  accentHover: "#1D4ED8",
  accentBg:    "#EFF6FF",
  success:     "#16A34A",
  successBg:   "#F0FDF4",
  warning:     "#D97706",
  warningBg:   "#FFFBEB",
  danger:      "#DC2626",
  dangerBg:    "#FEF2F2",
  primary:     "#0F172A",
  secondary:   "#475569",
  muted:       "#94A3B8",
  sidebarW:    240,
};

// ======================================================
// BASE STYLES
// ======================================================

const S = {
  input: {
    width: "100%",
    padding: "8px 12px",
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 6,
    color: C.primary,
    fontSize: 14,
    outline: "none",
    boxSizing: "border-box",
    fontFamily: "Inter, sans-serif",
    transition: "border-color 0.15s",
  },
  label: {
    display: "block",
    fontSize: 13,
    fontWeight: 500,
    color: C.secondary,
    marginBottom: 5,
  },
  formGroup: { marginBottom: 16 },
  card: {
    background: C.surface,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    padding: "20px 24px",
  },
  errorBox: {
    background: C.dangerBg,
    border: `1px solid #FCA5A5`,
    borderRadius: 6,
    padding: "10px 14px",
    color: C.danger,
    fontSize: 13,
    marginBottom: 16,
  },
};

// ======================================================
// BUTTON COMPONENT
// ======================================================

function Btn({ children, variant = "primary", size = "md", onClick, type = "button", disabled = false, style = {} }) {
  const base = {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    border: "1px solid",
    borderRadius: 6,
    cursor: disabled ? "not-allowed" : "pointer",
    fontFamily: "Inter, sans-serif",
    fontWeight: 500,
    transition: "background 0.15s, border-color 0.15s, color 0.15s",
    opacity: disabled ? 0.5 : 1,
    outline: "none",
    whiteSpace: "nowrap",
  };
  const sizes = {
    sm: { fontSize: 12, padding: "5px 12px", height: 28 },
    md: { fontSize: 14, padding: "7px 16px", height: 36 },
    lg: { fontSize: 14, padding: "10px 20px", height: 40 },
  };
  const variants = {
    primary:   { background: C.accent,   borderColor: C.accent,   color: "#fff" },
    secondary: { background: C.surface,  borderColor: C.border,   color: C.primary },
    danger:    { background: C.surface,  borderColor: C.danger,   color: C.danger },
    ghost:     { background: "transparent", borderColor: "transparent", color: C.secondary },
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{ ...base, ...sizes[size], ...variants[variant], ...style }}
    >
      {children}
    </button>
  );
}

// ======================================================
// BADGE COMPONENT
// ======================================================

function Badge({ label, variant = "default" }) {
  const map = {
    default:     { bg: "#F1F5F9", color: C.secondary },
    todo:        { bg: "#F1F5F9", color: C.secondary },
    in_progress: { bg: C.accentBg,  color: C.accent },
    done:        { bg: C.successBg, color: C.success },
    overdue:     { bg: C.dangerBg,  color: C.danger },
    active:      { bg: C.successBg, color: C.success },
    archived:    { bg: "#F1F5F9",   color: C.muted },
    completed:   { bg: C.accentBg,  color: C.accent },
    admin:       { bg: C.accentBg,  color: C.accent },
    member:      { bg: "#F1F5F9",   color: C.secondary },
    high:        { bg: C.dangerBg,  color: C.danger },
    medium:      { bg: C.warningBg, color: C.warning },
    low:         { bg: C.successBg, color: C.success },
  };
  const s = map[variant] || map.default;
  return (
    <span style={{
      background: s.bg,
      color: s.color,
      fontSize: 11,
      fontWeight: 600,
      padding: "2px 8px",
      borderRadius: 4,
      letterSpacing: "0.02em",
      textTransform: "capitalize",
      fontFamily: "Inter, sans-serif",
    }}>
      {label}
    </span>
  );
}

// ======================================================
// AVATAR
// ======================================================

function Avatar({ name, size = 32 }) {
  const initials = (name || "?").split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
  return (
    <div style={{
      width: size,
      height: size,
      borderRadius: "50%",
      background: "#E2E8F0",
      color: C.secondary,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontSize: size * 0.38,
      fontWeight: 600,
      flexShrink: 0,
      fontFamily: "Inter, sans-serif",
    }}>
      {initials}
    </div>
  );
}

// ======================================================
// SPINNER
// ======================================================

function Spinner({ size = 20 }) {
  return (
    <div style={{
      width: size, height: size,
      border: `2px solid ${C.border}`,
      borderTop: `2px solid ${C.accent}`,
      borderRadius: "50%",
      animation: "spin 0.7s linear infinite",
      flexShrink: 0,
    }} />
  );
}

function PageLoader() {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", minHeight: "100vh", background: C.bg }}>
      <Spinner size={32} />
    </div>
  );
}

// ======================================================
// SKELETON
// ======================================================

function SkeletonRow() {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 0", borderBottom: `1px solid ${C.border}` }}>
      <div className="skeleton" style={{ width: 32, height: 32, borderRadius: "50%" }} />
      <div style={{ flex: 1 }}>
        <div className="skeleton" style={{ height: 13, width: "60%", marginBottom: 6 }} />
        <div className="skeleton" style={{ height: 11, width: "35%" }} />
      </div>
    </div>
  );
}

// ======================================================
// EMPTY STATE
// ======================================================

function EmptyState({ title, subtitle }) {
  return (
    <div style={{ textAlign: "center", padding: "48px 24px" }}>
      <div style={{ width: 40, height: 40, borderRadius: 8, background: "#F1F5F9", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
        <svg width="20" height="20" fill="none" stroke={C.muted} strokeWidth="1.5" viewBox="0 0 24 24">
          <rect x="3" y="3" width="18" height="18" rx="2" /><path d="M9 9h6M9 12h6M9 15h4" />
        </svg>
      </div>
      <div style={{ fontSize: 14, fontWeight: 600, color: C.primary, marginBottom: 4 }}>{title}</div>
      {subtitle && <div style={{ fontSize: 13, color: C.muted }}>{subtitle}</div>}
    </div>
  );
}

// ======================================================
// SIDEBAR LAYOUT
// ======================================================

function Layout({ children }) {
  const { user, logout, token } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!token) return; // Don't fetch if no token

    API.get("/notifications/unread-count")
      .then(r => setUnread(r.data.unread_notifications || 0))
      .catch(() => {});
    const interval = setInterval(() => {
      API.get("/notifications/unread-count")
        .then(r => setUnread(r.data.unread_notifications || 0))
        .catch(() => {});
    }, 30000);
    return () => clearInterval(interval);
  }, [token]); // Add token as dependency

  const navItems = [
    {
      to: "/dashboard", label: "Dashboard",
      icon: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>,
    },
    {
      to: "/projects", label: "Projects",
      icon: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24"><path d="M3 7a2 2 0 012-2h3l2 2h9a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V7z"/></svg>,
    },
    {
      to: "/my-tasks", label: "My Tasks",
      icon: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>,
    },
    {
      to: "/notifications", label: "Notifications", badge: unread,
      icon: <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>,
    },
  ];

  const isActive = (to) => location.pathname === to || location.pathname.startsWith(to + "/");

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: C.bg }}>
      {/* Sidebar */}
      <aside style={{
        width: C.sidebarW,
        minHeight: "100vh",
        background: C.surface,
        borderRight: `1px solid ${C.border}`,
        display: "flex",
        flexDirection: "column",
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: 50,
      }}>
        {/* Logo */}
        <div style={{ padding: "20px 20px 16px", borderBottom: `1px solid ${C.border}` }}>
          <span style={{ fontSize: 16, fontWeight: 700, color: C.primary, letterSpacing: "-0.02em" }}>
            TaskFlow
          </span>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "12px 8px" }}>
          {navItems.map(item => {
            const active = isActive(item.to);
            return (
              <Link key={item.to} to={item.to} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "8px 12px",
                  borderRadius: 6,
                  marginBottom: 2,
                  background: active ? C.accentBg : "transparent",
                  color: active ? C.accent : C.secondary,
                  fontWeight: active ? 500 : 400,
                  fontSize: 14,
                  transition: "background 0.15s, color 0.15s",
                  cursor: "pointer",
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    {item.icon}
                    {item.label}
                  </div>
                  {item.badge > 0 && (
                    <span style={{
                      background: C.danger,
                      color: "#fff",
                      fontSize: 10,
                      fontWeight: 700,
                      padding: "1px 6px",
                      borderRadius: 10,
                      minWidth: 18,
                      textAlign: "center",
                    }}>{item.badge}</span>
                  )}
                </div>
              </Link>
            );
          })}
        </nav>

        {/* User at bottom */}
        <div style={{ padding: "12px 16px", borderTop: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
            <Avatar name={user?.name} size={30} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, color: C.primary, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{user?.name}</div>
              <div style={{ fontSize: 11, color: C.muted, textTransform: "capitalize" }}>{user?.role}</div>
            </div>
          </div>
          <button onClick={logout} style={{
            width: "100%",
            padding: "6px",
            background: "transparent",
            border: `1px solid ${C.border}`,
            borderRadius: 6,
            color: C.secondary,
            fontSize: 13,
            cursor: "pointer",
            fontFamily: "Inter, sans-serif",
            transition: "border-color 0.15s, color 0.15s",
          }}>
            Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main style={{ marginLeft: C.sidebarW, flex: 1, minHeight: "100vh" }}>
        {children}
      </main>
    </div>
  );
}

// ======================================================
// PAGE HEADER
// ======================================================

function PageHeader({ title, subtitle, breadcrumb, action }) {
  return (
    <div style={{
      background: C.surface,
      borderBottom: `1px solid ${C.border}`,
      padding: "0 32px",
      height: 64,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      position: "sticky",
      top: 0,
      zIndex: 40,
    }}>
      <div>
        {breadcrumb && (
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 2 }}>
            {breadcrumb}
          </div>
        )}
        <h1 style={{ fontSize: 17, fontWeight: 600, color: C.primary, lineHeight: 1.2 }}>{title}</h1>
        {subtitle && <p style={{ fontSize: 13, color: C.muted, marginTop: 1 }}>{subtitle}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}

// ======================================================
// AUTH PAGES — SHARED SHELL
// ======================================================

function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div style={{ minHeight: "100vh", background: C.bg, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 400 }}>
        <div style={{ marginBottom: 32, textAlign: "center" }}>
          <div style={{ fontSize: 18, fontWeight: 700, color: C.primary, marginBottom: 4 }}>TaskFlow</div>
          <div style={{ fontSize: 22, fontWeight: 600, color: C.primary, marginBottom: 4 }}>{title}</div>
          <div style={{ fontSize: 14, color: C.muted }}>{subtitle}</div>
        </div>
        <div style={{ ...S.card, boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
          {children}
        </div>
        {footer && <div style={{ textAlign: "center", marginTop: 20, fontSize: 13, color: C.muted }}>{footer}</div>}
      </div>
    </div>
  );
}

// ======================================================
// SIGNUP PAGE
// ======================================================

function SignupPage() {
  const navigate = useNavigate();
  const [form, setForm]       = useState({ name: "", email: "", password: "", role: "member" });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      await API.post("/signup", form);
      navigate("/login");
    } catch (err) {
      setError(err.response?.data?.detail || "Signup failed. Please try again.");
    } finally { setLoading(false); }
  };

  return (
    <AuthShell
      title="Create your account"
      subtitle="Get started with TaskFlow"
      footer={<>Already have an account? <Link to="/login" style={{ color: C.accent, textDecoration: "none", fontWeight: 500 }}>Sign in</Link></>}
    >
      {error && <div style={S.errorBox}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div style={S.formGroup}>
          <label style={S.label}>Full name</label>
          <input style={S.input} placeholder="Alex Johnson" value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })} required />
        </div>
        <div style={S.formGroup}>
          <label style={S.label}>Email address</label>
          <input style={S.input} type="email" placeholder="alex@company.com" value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })} required />
        </div>
        <div style={S.formGroup}>
          <label style={S.label}>Password</label>
          <input style={S.input} type="password" placeholder="At least 8 characters" value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })} required />
        </div>
        <div style={S.formGroup}>
          <label style={S.label}>Role</label>
          <select style={S.input} value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
            <option value="member">Member</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <Btn type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center" }}>
          {loading ? <><Spinner size={14} /> Creating account...</> : "Create account"}
        </Btn>
      </form>
    </AuthShell>
  );
}

// ======================================================
// LOGIN PAGE
// ======================================================

function LoginPage() {
  const navigate      = useNavigate();
  const { login }     = useAuth();
  const [form, setForm]         = useState({ email: "", password: "" });
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");
  const [showPassword, setShowPassword] = useState(false); // 👈 ADD THIS

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      const res = await API.post("/login", form);
      login(res.data.access_token, res.data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid credentials.");
    } finally { setLoading(false); }
  };

  return (
    <AuthShell
      title="Sign in"
      subtitle="Welcome back to TaskFlow"
      footer={<>Don't have an account? <Link to="/signup" style={{ color: C.accent, textDecoration: "none", fontWeight: 500 }}>Sign up</Link></>}
    >
      {error && <div style={S.errorBox}>{error}</div>}
      <form onSubmit={handleSubmit}>
        <div style={S.formGroup}>
          <label style={S.label}>Email address</label>
          <input style={S.input} type="email" placeholder="alex@company.com" value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })} required />
        </div>

        {/* 👇 REPLACE password field with this */}
        <div style={S.formGroup}>
          <label style={S.label}>Password</label>
          <div style={{ position: "relative" }}>
            <input
              style={{ ...S.input, paddingRight: 40 }}
              type={showPassword ? "text" : "password"}
              placeholder="Your password"
              value={form.password}
              onChange={e => setForm({ ...form, password: e.target.value })}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: "absolute",
                right: 10,
                top: "50%",
                transform: "translateY(-50%)",
                background: "none",
                border: "none",
                cursor: "pointer",
                color: C.muted,
                padding: 0,
                display: "flex",
                alignItems: "center",
              }}
            >
              {showPassword ? (
                // Eye-off icon (hide)
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                  <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/>
                  <path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              ) : (
                // Eye icon (show)
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        <Btn type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center" }}>
          {loading ? <><Spinner size={14} /> Signing in...</> : "Sign in"}
        </Btn>
      </form>
    </AuthShell>
  );
}

// ======================================================
// STAT CARD
// ======================================================

function StatCard({ label, value, accentColor }) {
  return (
    <div style={{
      ...S.card,
      borderTop: `3px solid ${accentColor}`,
      padding: "20px 24px",
    }}>
      <div style={{ fontSize: 28, fontWeight: 700, color: C.primary, lineHeight: 1, marginBottom: 6 }}>
        {value ?? "—"}
      </div>
      <div style={{ fontSize: 13, color: C.secondary }}>{label}</div>
    </div>
  );
}

// ======================================================
// DASHBOARD PAGE
// ======================================================

function DashboardPage() {
  const { user }   = useAuth();
  const navigate   = useNavigate();
  const [summary,  setSummary]  = useState(null);
  const [recent,   setRecent]   = useState([]);
  const [overdue,  setOverdue]  = useState([]);
  const [loading,  setLoading]  = useState(true);

  useEffect(() => {
    Promise.all([
      API.get("/dashboard/summary"),
      API.get("/dashboard/recent-tasks"),
      API.get("/dashboard/overdue-tasks"),
    ]).then(([s, r, o]) => {
      setSummary(s.data);
      setRecent(r.data);
      setOverdue(o.data);
    }).catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const statusVariant = (s) => s === "done" ? "done" : s === "in_progress" ? "in_progress" : "todo";
  const priorityVariant = (p) => p === "high" ? "high" : p === "medium" ? "medium" : "low";

  return (
    <Layout>
      <PageHeader
        title="Dashboard"
        subtitle={`${new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" })}`}
        action={user?.role === "admin" && (
          <Btn onClick={() => navigate("/projects")}>New project</Btn>
        )}
      />
      <div style={{ padding: "28px 32px", maxWidth: 1100 }}>

        {loading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 16, marginBottom: 28 }}>
            {[...Array(5)].map((_, i) => (
              <div key={i} style={{ ...S.card, height: 88 }}>
                <div className="skeleton" style={{ height: 28, width: 60, marginBottom: 8 }} />
                <div className="skeleton" style={{ height: 13, width: 80 }} />
              </div>
            ))}
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 16, marginBottom: 28 }}>
            <StatCard label="Total projects"   value={summary?.total_projects}  accentColor={C.accent} />
            <StatCard label="Total tasks"      value={summary?.total_tasks}     accentColor={C.border} />
            <StatCard label="Completed"        value={summary?.completed_tasks} accentColor={C.success} />
            <StatCard label="Pending"          value={summary?.pending_tasks}   accentColor={C.warning} />
            <StatCard label="Overdue"          value={summary?.overdue_tasks}   accentColor={C.danger} />
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>

          {/* Recent Tasks */}
          <div style={S.card}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: C.primary }}>Recent tasks</div>
              <Link to="/my-tasks" style={{ fontSize: 13, color: C.accent, textDecoration: "none" }}>View all</Link>
            </div>
            {loading ? (
              [...Array(4)].map((_, i) => <SkeletonRow key={i} />)
            ) : recent.length === 0 ? (
              <EmptyState title="No tasks yet" subtitle="Tasks will appear here once created" />
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse" }}>
                <thead>
                  <tr style={{ background: C.bg }}>
                    {["Task", "Status", "Priority", "Due"].map(h => (
                      <th key={h} style={{ textAlign: "left", padding: "8px 10px", fontSize: 11, fontWeight: 600, color: C.muted, textTransform: "uppercase", letterSpacing: "0.05em" }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recent.slice(0, 6).map(task => (
                    <tr key={task.id} style={{ borderBottom: `1px solid ${C.border}` }}>
                      <td style={{ padding: "10px 10px", fontSize: 14, color: C.primary, fontWeight: 500, maxWidth: 180, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{task.title}</td>
                      <td style={{ padding: "10px 10px" }}><Badge label={task.status.replace("_", " ")} variant={statusVariant(task.status)} /></td>
                      <td style={{ padding: "10px 10px" }}><Badge label={task.priority} variant={priorityVariant(task.priority)} /></td>
                      <td style={{ padding: "10px 10px", fontSize: 12, color: C.muted }}>{task.due_date || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Overdue Tasks */}
          <div style={{ ...S.card, borderTop: `3px solid ${C.danger}` }}>
            <div style={{ fontSize: 14, fontWeight: 600, color: C.primary, marginBottom: 16 }}>Overdue tasks</div>
            {loading ? (
              [...Array(3)].map((_, i) => <SkeletonRow key={i} />)
            ) : overdue.length === 0 ? (
              <EmptyState title="No overdue tasks" subtitle="You are all caught up" />
            ) : overdue.map(task => (
              <div key={task.id} style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                padding: "10px 0",
                borderBottom: `1px solid ${C.border}`,
              }}>
                <div>
                  <div style={{ fontSize: 14, fontWeight: 500, color: C.primary, marginBottom: 3 }}>{task.title}</div>
                  <Badge label={task.priority} variant={priorityVariant(task.priority)} />
                </div>
                <div style={{ fontSize: 12, color: C.danger, fontWeight: 500 }}>Due {task.due_date}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}

// ======================================================
// PROJECTS PAGE
// ======================================================

function ProjectsPage() {
  const { user }    = useAuth();
  const navigate    = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading,  setLoading]  = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm]         = useState({ name: "", description: "", status: "active", deadline: "" });
  const [formErr, setFormErr]   = useState("");
  const [saving,  setSaving]    = useState(false);

  const fetchProjects = async () => {
    try {
      const res = await API.get("/projects");
      setProjects(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchProjects(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    setSaving(true); setFormErr("");
    try {
      await API.post("/projects", { ...form, deadline: form.deadline || null });
      setShowForm(false);
      setForm({ name: "", description: "", status: "active", deadline: "" });
      fetchProjects();
    } catch (err) {
      setFormErr(err.response?.data?.detail || "Failed to create project");
    } finally { setSaving(false); }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this project? This cannot be undone.")) return;
    try {
      await API.delete(`/projects/${id}`);
      fetchProjects();
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  return (
    <Layout>
      <PageHeader
        title="Projects"
        subtitle={`${projects.length} project${projects.length !== 1 ? "s" : ""}`}
        action={user?.role === "admin" && (
          <Btn onClick={() => setShowForm(!showForm)}>
            {showForm ? "Cancel" : "New project"}
          </Btn>
        )}
      />
      <div style={{ padding: "28px 32px", maxWidth: 1100 }}>

        {/* Create Form */}
        {showForm && (
          <div style={{ ...S.card, marginBottom: 24 }} className="fade-in">
            <div style={{ fontSize: 15, fontWeight: 600, color: C.primary, marginBottom: 20 }}>New project</div>
            {formErr && <div style={S.errorBox}>{formErr}</div>}
            <form onSubmit={handleCreate}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div style={S.formGroup}>
                  <label style={S.label}>Project name</label>
                  <input style={S.input} placeholder="e.g. Website Redesign" value={form.name}
                    onChange={e => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div style={S.formGroup}>
                  <label style={S.label}>Deadline</label>
                  <input style={S.input} type="date" value={form.deadline}
                    onChange={e => setForm({ ...form, deadline: e.target.value })} />
                </div>
              </div>
              <div style={S.formGroup}>
                <label style={S.label}>Description</label>
                <textarea style={{ ...S.input, minHeight: 72, resize: "vertical" }}
                  placeholder="What is this project about?" value={form.description}
                  onChange={e => setForm({ ...form, description: e.target.value })} />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <Btn type="submit" disabled={saving}>
                  {saving ? <><Spinner size={13} /> Creating...</> : "Create project"}
                </Btn>
                <Btn variant="secondary" onClick={() => setShowForm(false)}>Cancel</Btn>
              </div>
            </form>
          </div>
        )}

        {loading ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
            {[...Array(3)].map((_, i) => (
              <div key={i} style={{ ...S.card, height: 160 }}>
                <div className="skeleton" style={{ height: 16, width: "70%", marginBottom: 10 }} />
                <div className="skeleton" style={{ height: 12, width: "40%", marginBottom: 20 }} />
                <div className="skeleton" style={{ height: 12, width: "90%" }} />
              </div>
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div style={S.card}>
            <EmptyState title="No projects yet" subtitle={user?.role === "admin" ? "Create your first project to get started" : "You have not been added to any projects yet"} />
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 16 }}>
            {projects.map(p => (
              <div key={p.id} style={{
                ...S.card,
                transition: "border-color 0.15s",
                cursor: "pointer",
              }}
                onMouseEnter={e => e.currentTarget.style.borderColor = C.borderHover}
                onMouseLeave={e => e.currentTarget.style.borderColor = C.border}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                  <div style={{ fontSize: 15, fontWeight: 600, color: C.primary }}>{p.name}</div>
                  <Badge label={p.status} variant={p.status} />
                </div>
                <div style={{ fontSize: 13, color: C.secondary, marginBottom: 16, minHeight: 36, lineHeight: 1.5 }}>
                  {p.description || "No description provided"}
                </div>
                {p.deadline && (
                  <div style={{ fontSize: 12, color: C.muted, marginBottom: 16 }}>
                    Deadline: {p.deadline}
                  </div>
                )}
                <div style={{ display: "flex", gap: 8, justifyContent: "space-between", alignItems: "center" }}>
                  <Btn onClick={() => navigate(`/projects/${p.id}`)} size="sm">Open project</Btn>
                  {user?.role === "admin" && (
                    <Btn variant="danger" size="sm" onClick={() => handleDelete(p.id)}>Delete</Btn>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}

// ======================================================
// PROJECT DETAIL PAGE
// ======================================================

function ProjectDetailPage() {
  const { projectId } = useParams();
  const { user }      = useAuth();
  const [project, setProject]   = useState(null);
  const [tasks,   setTasks]     = useState([]);
  const [members, setMembers]   = useState([]);
  const [allUsers, setAllUsers] = useState([]);
  const [tab, setTab]           = useState("tasks");
  const [loading, setLoading]   = useState(true);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [taskForm, setTaskForm] = useState({ title: "", description: "", priority: "medium", due_date: "", assignee_id: "" });
  const [taskErr, setTaskErr]   = useState("");
  const [saving,  setSaving]    = useState(false);
  const [memberEmail, setMemberEmail] = useState("");
  const [memberRole,  setMemberRole]  = useState("member");
  const [memberErr,   setMemberErr]   = useState("");

  const fetchAll = useCallback(async () => {
    try {
      const [proj, t, m] = await Promise.all([
        API.get(`/projects/${projectId}`),
        API.get(`/projects/${projectId}/tasks`),
        API.get(`/projects/${projectId}/members`),
      ]);
      setProject(proj.data);
      setTasks(t.data);
      setMembers(m.data);
      if (user?.role === "admin") {
        const usersRes = await API.get("/users").catch(() => ({ data: [] }));
        setAllUsers(usersRes.data);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  }, [projectId, user]);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const handleCreateTask = async (e) => {
    e.preventDefault();
    setSaving(true); setTaskErr("");
    try {
      await API.post("/tasks", {
        ...taskForm,
        project_id: projectId,
        due_date:    taskForm.due_date   || null,
        assignee_id: taskForm.assignee_id || null,
      });
      setShowTaskForm(false);
      setTaskForm({ title: "", description: "", priority: "medium", due_date: "", assignee_id: "" });
      fetchAll();
    } catch (err) {
      setTaskErr(err.response?.data?.detail || "Failed to create task");
    } finally { setSaving(false); }
  };

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await API.patch(`/tasks/${taskId}/status`, { status: newStatus });
      fetchAll();
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  const handleDeleteTask = async (taskId) => {
    if (!confirm("Delete this task?")) return;
    try {
      await API.delete(`/tasks/${taskId}`);
      fetchAll();
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    setMemberErr("");
    const found = allUsers.find(u => u.email === memberEmail);
    if (!found) { setMemberErr("No user found with that email address"); return; }
    try {
      await API.post(`/projects/${projectId}/members`, { user_id: found.id, role: memberRole });
      setMemberEmail("");
      fetchAll();
    } catch (err) { setMemberErr(err.response?.data?.detail || "Failed"); }
  };

  const handleRemoveMember = async (userId) => {
    if (!confirm("Remove this member from the project?")) return;
    try {
      await API.delete(`/projects/${projectId}/members/${userId}`);
      fetchAll();
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  const statusVariant   = (s) => s === "done" ? "done" : s === "in_progress" ? "in_progress" : "todo";
  const priorityVariant = (p) => p === "high" ? "high" : p === "medium" ? "medium" : "low";
  const priorityBorder  = (p) => p === "high" ? C.danger : p === "medium" ? C.warning : C.success;

  const grouped = {
    todo:        tasks.filter(t => t.status === "todo"),
    in_progress: tasks.filter(t => t.status === "in_progress"),
    done:        tasks.filter(t => t.status === "done"),
    overdue:     tasks.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.status !== "done"),
  };

  const columns = [
    { key: "todo",        label: "To do",       color: C.muted    },
    { key: "in_progress", label: "In progress", color: C.accent   },
    { key: "done",        label: "Done",        color: C.success  },
    { key: "overdue",     label: "Overdue",     color: C.danger   },
  ];

  if (loading) return <Layout><PageLoader /></Layout>;

  return (
    <Layout>
      <PageHeader
        title={project?.name}
        subtitle={project?.description}
        breadcrumb={
          <>
            <Link to="/projects" style={{ fontSize: 13, color: C.muted, textDecoration: "none" }}>Projects</Link>
            <span style={{ color: C.muted, fontSize: 13 }}>/</span>
            <span style={{ fontSize: 13, color: C.secondary }}>{project?.name}</span>
          </>
        }
        action={
          tab === "tasks" && (
            <Btn onClick={() => setShowTaskForm(!showTaskForm)}>
              {showTaskForm ? "Cancel" : "Add task"}
            </Btn>
          )
        }
      />

      <div style={{ padding: "0 32px 32px", maxWidth: 1200 }}>

        {/* Tabs */}
        <div style={{ display: "flex", borderBottom: `1px solid ${C.border}`, marginBottom: 24, paddingTop: 20 }}>
          {[
            { key: "tasks",   label: `Tasks (${tasks.length})` },
            { key: "members", label: `Members (${members.length})` },
          ].map(t => (
            <button key={t.key} onClick={() => setTab(t.key)} style={{
              padding: "10px 16px",
              background: "none",
              border: "none",
              borderBottom: tab === t.key ? `2px solid ${C.accent}` : "2px solid transparent",
              color: tab === t.key ? C.accent : C.secondary,
              fontWeight: tab === t.key ? 600 : 400,
              fontSize: 14,
              cursor: "pointer",
              marginBottom: -1,
              fontFamily: "Inter, sans-serif",
              transition: "color 0.15s",
            }}>
              {t.label}
            </button>
          ))}
        </div>

        {/* Task Creation Form */}
        {tab === "tasks" && showTaskForm && (
          <div style={{ ...S.card, marginBottom: 24 }} className="fade-in">
            <div style={{ fontSize: 15, fontWeight: 600, color: C.primary, marginBottom: 20 }}>New task</div>
            {taskErr && <div style={S.errorBox}>{taskErr}</div>}
            <form onSubmit={handleCreateTask}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <div style={S.formGroup}>
                  <label style={S.label}>Title</label>
                  <input style={S.input} placeholder="Task title" value={taskForm.title}
                    onChange={e => setTaskForm({ ...taskForm, title: e.target.value })} required />
                </div>
                <div style={S.formGroup}>
                  <label style={S.label}>Priority</label>
                  <select style={S.input} value={taskForm.priority}
                    onChange={e => setTaskForm({ ...taskForm, priority: e.target.value })}>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div style={S.formGroup}>
                  <label style={S.label}>Due date</label>
                  <input style={S.input} type="date" value={taskForm.due_date}
                    onChange={e => setTaskForm({ ...taskForm, due_date: e.target.value })} />
                </div>
                <div style={S.formGroup}>
                  <label style={S.label}>Assignee</label>
                  <select style={S.input} value={taskForm.assignee_id}
                    onChange={e => setTaskForm({ ...taskForm, assignee_id: e.target.value })}>
                    <option value="">Unassigned</option>
                    {members.map(m => {
                      const u = allUsers.find(u => u.id === m.user_id);
                      return u ? <option key={m.user_id} value={m.user_id}>{u.name}</option> : null;
                    })}
                  </select>
                </div>
              </div>
              <div style={S.formGroup}>
                <label style={S.label}>Description</label>
                <textarea style={{ ...S.input, minHeight: 64, resize: "vertical" }}
                  placeholder="Optional details..." value={taskForm.description}
                  onChange={e => setTaskForm({ ...taskForm, description: e.target.value })} />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <Btn type="submit" disabled={saving}>
                  {saving ? <><Spinner size={13} /> Creating...</> : "Create task"}
                </Btn>
                <Btn variant="secondary" onClick={() => setShowTaskForm(false)}>Cancel</Btn>
              </div>
            </form>
          </div>
        )}

        {/* Kanban Board */}
        {tab === "tasks" && (
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr 1fr", gap: 16 }}>
            {columns.map(col => (
              <div key={col.key}>
                {/* Column header */}
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <span style={{
                    fontSize: 11,
                    fontWeight: 700,
                    textTransform: "uppercase",
                    letterSpacing: "0.06em",
                    color: col.color,
                  }}>{col.label}</span>
                  <span style={{
                    background: C.bg,
                    border: `1px solid ${C.border}`,
                    color: C.secondary,
                    fontSize: 11,
                    fontWeight: 600,
                    padding: "1px 7px",
                    borderRadius: 10,
                  }}>{grouped[col.key].length}</span>
                </div>

                {/* Cards */}
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {grouped[col.key].length === 0 ? (
                    <div style={{
                      border: `1px dashed ${C.border}`,
                      borderRadius: 8,
                      padding: "20px 12px",
                      textAlign: "center",
                      color: C.muted,
                      fontSize: 12,
                    }}>No tasks</div>
                  ) : grouped[col.key].map(task => (
                    <div key={task.id} style={{
                      background: C.surface,
                      border: `1px solid ${C.border}`,
                      borderLeft: `3px solid ${priorityBorder(task.priority)}`,
                      borderRadius: 8,
                      padding: "12px 14px",
                      transition: "border-color 0.15s",
                    }}
                      onMouseEnter={e => e.currentTarget.style.borderColor = C.borderHover}
                      onMouseLeave={e => e.currentTarget.style.borderColor = C.border}
                    >
                      <div style={{ fontSize: 13, fontWeight: 600, color: C.primary, marginBottom: 8, lineHeight: 1.4 }}>{task.title}</div>
                      {task.description && (
                        <div style={{ fontSize: 12, color: C.secondary, marginBottom: 8, lineHeight: 1.4, overflow: "hidden", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" }}>
                          {task.description}
                        </div>
                      )}
                      <div style={{ display: "flex", gap: 6, marginBottom: 10, flexWrap: "wrap", alignItems: "center" }}>
                        <Badge label={task.priority} variant={priorityVariant(task.priority)} />
                        {task.due_date && (
                          <span style={{ fontSize: 11, color: C.muted }}>{task.due_date}</span>
                        )}
                      </div>
                      {col.key !== "done" && col.key !== "overdue" && (
                        <select
                          value={task.status}
                          onChange={e => handleStatusChange(task.id, e.target.value)}
                          style={{ ...S.input, padding: "5px 8px", fontSize: 12, marginBottom: 8 }}
                        >
                          <option value="todo">To do</option>
                          <option value="in_progress">In progress</option>
                          <option value="done">Done</option>
                        </select>
                      )}
                      {col.key === "overdue" && (
                        <select
                          value={task.status}
                          onChange={e => handleStatusChange(task.id, e.target.value)}
                          style={{ ...S.input, padding: "5px 8px", fontSize: 12, marginBottom: 8 }}
                        >
                          <option value="todo">To do</option>
                          <option value="in_progress">In progress</option>
                          <option value="done">Done</option>
                        </select>
                      )}
                      {user?.role === "admin" && (
                        <Btn variant="danger" size="sm" style={{ width: "100%", justifyContent: "center" }}
                          onClick={() => handleDeleteTask(task.id)}>
                          Delete
                        </Btn>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Members Tab */}
        {tab === "members" && (
          <div style={{ maxWidth: 640 }}>
            {user?.role === "admin" && (
              <div style={{ ...S.card, marginBottom: 20 }}>
                <div style={{ fontSize: 15, fontWeight: 600, color: C.primary, marginBottom: 16 }}>Add member</div>
                {memberErr && <div style={S.errorBox}>{memberErr}</div>}
                <form onSubmit={handleAddMember} style={{ display: "flex", gap: 10 }}>
                  <input style={{ ...S.input, flex: 1 }} placeholder="Email address" value={memberEmail}
                    onChange={e => setMemberEmail(e.target.value)} required />
                  <select style={{ ...S.input, width: 120 }} value={memberRole}
                    onChange={e => setMemberRole(e.target.value)}>
                    <option value="member">Member</option>
                    <option value="admin">Admin</option>
                  </select>
                  <Btn type="submit">Add</Btn>
                </form>
              </div>
            )}

            <div style={S.card}>
              <div style={{ fontSize: 15, fontWeight: 600, color: C.primary, marginBottom: 4 }}>Team members</div>
              <div style={{ fontSize: 13, color: C.muted, marginBottom: 16 }}>{members.length} member{members.length !== 1 ? "s" : ""}</div>
              {members.length === 0 ? (
                <EmptyState title="No members yet" subtitle="Add team members to collaborate on this project" />
              ) : members.map(m => {
                const u = allUsers.find(u => u.id === m.user_id);
                return (
                  <div key={m.id} style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "12px 0",
                    borderBottom: `1px solid ${C.border}`,
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      <Avatar name={u?.name || "?"} size={36} />
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 500, color: C.primary }}>{u?.name || m.user_id}</div>
                        <div style={{ fontSize: 12, color: C.muted }}>{u?.email}</div>
                      </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <Badge label={m.role} variant={m.role} />
                      {user?.role === "admin" && m.user_id !== user?.id && (
                        <Btn variant="danger" size="sm" onClick={() => handleRemoveMember(m.user_id)}>Remove</Btn>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}

// ======================================================
// MY TASKS PAGE
// ======================================================

function MyTasksPage() {
  const [tasks,   setTasks]   = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter,  setFilter]  = useState("all");

  useEffect(() => {
    API.get("/tasks/my-tasks")
      .then(r => setTasks(r.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleStatusChange = async (taskId, newStatus) => {
    try {
      await API.patch(`/tasks/${taskId}/status`, { status: newStatus });
      const res = await API.get("/tasks/my-tasks");
      setTasks(res.data);
    } catch (err) { alert(err.response?.data?.detail || "Failed"); }
  };

  const filtered = filter === "all"     ? tasks
    : filter === "overdue" ? tasks.filter(t => t.due_date && new Date(t.due_date) < new Date() && t.status !== "done")
    : tasks.filter(t => t.status === filter);

  const statusVariant   = (s) => s === "done" ? "done" : s === "in_progress" ? "in_progress" : "todo";
  const priorityVariant = (p) => p === "high" ? "high" : p === "medium" ? "medium" : "low";
  const priorityBorder  = (p) => p === "high" ? C.danger : p === "medium" ? C.warning : C.success;

  const filterLabels = {
    all: "All", todo: "To do", in_progress: "In progress", done: "Done", overdue: "Overdue"
  };

  return (
    <Layout>
      <PageHeader
        title="My Tasks"
        subtitle={`${filtered.length} task${filtered.length !== 1 ? "s" : ""}`}
      />
      <div style={{ padding: "28px 32px", maxWidth: 900 }}>

        {/* Filter tabs */}
        <div style={{ display: "flex", gap: 6, marginBottom: 24, flexWrap: "wrap" }}>
          {Object.entries(filterLabels).map(([key, label]) => (
            <button key={key} onClick={() => setFilter(key)} style={{
              padding: "5px 14px",
              borderRadius: 6,
              border: `1px solid ${filter === key ? C.accent : C.border}`,
              background: filter === key ? C.accentBg : C.surface,
              color: filter === key ? C.accent : C.secondary,
              fontWeight: filter === key ? 500 : 400,
              fontSize: 13,
              cursor: "pointer",
              fontFamily: "Inter, sans-serif",
              transition: "all 0.15s",
            }}>
              {label}
            </button>
          ))}
        </div>

        {loading ? (
          <div style={S.card}>{[...Array(4)].map((_, i) => <SkeletonRow key={i} />)}</div>
        ) : filtered.length === 0 ? (
          <div style={S.card}>
            <EmptyState title="No tasks found" subtitle="Tasks assigned to you will appear here" />
          </div>
        ) : (
          <div style={S.card}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: C.bg }}>
                  {["Task", "Status", "Priority", "Due date", "Action"].map(h => (
                    <th key={h} style={{ textAlign: "left", padding: "9px 14px", fontSize: 11, fontWeight: 600, color: C.muted, textTransform: "uppercase", letterSpacing: "0.05em", borderBottom: `1px solid ${C.border}` }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map(task => {
                  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== "done";
                  return (
                    <tr key={task.id} style={{ borderBottom: `1px solid ${C.border}`, transition: "background 0.1s" }}
                      onMouseEnter={e => e.currentTarget.style.background = C.bg}
                      onMouseLeave={e => e.currentTarget.style.background = "transparent"}
                    >
                      <td style={{ padding: "12px 14px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                          <div style={{ width: 3, height: 32, borderRadius: 2, background: priorityBorder(task.priority), flexShrink: 0 }} />
                          <div>
                            <div style={{ fontSize: 14, fontWeight: 500, color: C.primary }}>{task.title}</div>
                            {task.description && (
                              <div style={{ fontSize: 12, color: C.muted, marginTop: 2 }}>{task.description.slice(0, 60)}{task.description.length > 60 ? "..." : ""}</div>
                            )}
                          </div>
                        </div>
                      </td>
                      <td style={{ padding: "12px 14px" }}>
                        <Badge label={task.status.replace("_", " ")} variant={statusVariant(task.status)} />
                      </td>
                      <td style={{ padding: "12px 14px" }}>
                        <Badge label={task.priority} variant={priorityVariant(task.priority)} />
                      </td>
                      <td style={{ padding: "12px 14px", fontSize: 13, color: isOverdue ? C.danger : C.secondary, fontWeight: isOverdue ? 500 : 400 }}>
                        {task.due_date || "—"}
                      </td>
                      <td style={{ padding: "12px 14px" }}>
                        {task.status !== "done" ? (
                          <select value={task.status} onChange={e => handleStatusChange(task.id, e.target.value)}
                            style={{ ...S.input, width: 140, padding: "5px 8px", fontSize: 12 }}>
                            <option value="todo">To do</option>
                            <option value="in_progress">In progress</option>
                            <option value="done">Done</option>
                          </select>
                        ) : (
                          <span style={{ fontSize: 13, color: C.success, fontWeight: 500 }}>Completed</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}

// ======================================================
// NOTIFICATIONS PAGE
// ======================================================

function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading]             = useState(true);

  const fetchNotifs = async () => {
    try {
      const res = await API.get("/notifications");
      setNotifications(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchNotifs(); }, []);

  const markAllRead = async () => {
    await API.patch("/notifications/mark-all-read").catch(() => {});
    fetchNotifs();
  };

  const markRead = async (id) => {
    await API.patch(`/notifications/${id}/read`).catch(() => {});
    fetchNotifs();
  };

  const deleteNotif = async (id) => {
    await API.delete(`/notifications/${id}`).catch(() => {});
    fetchNotifs();
  };

  const clearAll = async () => {
    if (!confirm("Clear all notifications?")) return;
    await API.delete("/notifications/clear-all").catch(() => {});
    fetchNotifs();
  };

  const typeVariant = {
    task_assigned:  { label: "Assigned",      color: C.accent },
    task_updated:   { label: "Updated",       color: C.warning },
    comment_added:  { label: "Comment",       color: C.secondary },
    project_invite: { label: "Invited",       color: C.success },
    due_soon:       { label: "Due soon",      color: C.warning },
    overdue:        { label: "Overdue",       color: C.danger },
  };

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <Layout>
      <PageHeader
        title="Notifications"
        subtitle={unreadCount > 0 ? `${unreadCount} unread` : "All caught up"}
        action={
          <div style={{ display: "flex", gap: 8 }}>
            <Btn variant="secondary" size="sm" onClick={markAllRead}>Mark all read</Btn>
            <Btn variant="danger"    size="sm" onClick={clearAll}>Clear all</Btn>
          </div>
        }
      />
      <div style={{ padding: "28px 32px", maxWidth: 700 }}>
        {loading ? (
          <div style={S.card}>{[...Array(4)].map((_, i) => <SkeletonRow key={i} />)}</div>
        ) : notifications.length === 0 ? (
          <div style={S.card}>
            <EmptyState title="No notifications" subtitle="You are all caught up" />
          </div>
        ) : (
          <div style={S.card}>
            {notifications.map((n, i) => {
              const meta = typeVariant[n.type] || { label: n.type, color: C.secondary };
              return (
                <div key={n.id} style={{
                  display: "flex",
                  alignItems: "flex-start",
                  gap: 14,
                  padding: "14px 0",
                  borderBottom: i < notifications.length - 1 ? `1px solid ${C.border}` : "none",
                  opacity: n.is_read ? 0.55 : 1,
                  transition: "opacity 0.15s",
                }}>
                  {/* Dot indicator */}
                  <div style={{
                    width: 8, height: 8, borderRadius: "50%",
                    background: n.is_read ? C.border : meta.color,
                    marginTop: 5, flexShrink: 0,
                  }} />

                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
                      <span style={{ fontSize: 13, fontWeight: n.is_read ? 400 : 500, color: C.primary }}>{n.message}</span>
                      <span style={{
                        fontSize: 11,
                        fontWeight: 500,
                        color: meta.color,
                        background: meta.color + "15",
                        padding: "1px 7px",
                        borderRadius: 4,
                        flexShrink: 0,
                      }}>{meta.label}</span>
                    </div>
                    <div style={{ fontSize: 12, color: C.muted }}>
                      {new Date(n.created_at).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </div>
                  </div>

                  <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                    {!n.is_read && (
                      <Btn variant="secondary" size="sm" onClick={() => markRead(n.id)}>Read</Btn>
                    )}
                    <Btn variant="ghost" size="sm" onClick={() => deleteNotif(n.id)} style={{ color: C.muted }}>
                      <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.75" viewBox="0 0 24 24">
                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                      </svg>
                    </Btn>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Layout>
  );
}

// ======================================================
// APP ROUTER
// ======================================================

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/"                    element={<Navigate to="/login" />} />
          <Route path="/signup"              element={<SignupPage />} />
          <Route path="/login"               element={<LoginPage />} />
          <Route path="/dashboard"           element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/projects"            element={<ProtectedRoute><ProjectsPage /></ProtectedRoute>} />
          <Route path="/projects/:projectId" element={<ProtectedRoute><ProjectDetailPage /></ProtectedRoute>} />
          <Route path="/my-tasks"            element={<ProtectedRoute><MyTasksPage /></ProtectedRoute>} />
          <Route path="/notifications"       element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
          <Route path="*"                    element={<Navigate to="/dashboard" />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

// ======================================================
// RENDER
// ======================================================

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
