import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Meters from './pages/Meters'
import Purchase from './pages/Purchase'
import Transactions from './pages/Transactions'
import TokenHistory from './pages/TokenHistory'
import AdminDashboard from './pages/AdminDashboard'
import AdminCustomers from './pages/AdminCustomers'
import AdminTransactions from './pages/AdminTransactions'
import AdminReports from './pages/AdminReports'
import AdminSettings from './pages/AdminSettings'
import LoadingSpinner from './components/LoadingSpinner'

function PrivateRoute({ children, adminOnly = false }) {
  const { user, loading, isAdmin } = useAuth()
  if (loading) return <LoadingSpinner fullScreen />
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && !isAdmin) return <Navigate to="/" replace />
  return children
}

function PublicRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <LoadingSpinner fullScreen />
  if (user) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
      <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
      <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
        <Route index element={<Dashboard />} />
        <Route path="meters" element={<Meters />} />
        <Route path="purchase" element={<Purchase />} />
        <Route path="transactions" element={<Transactions />} />
        <Route path="tokens" element={<TokenHistory />} />
        <Route path="admin" element={<PrivateRoute adminOnly><AdminDashboard /></PrivateRoute>} />
        <Route path="admin/customers" element={<PrivateRoute adminOnly><AdminCustomers /></PrivateRoute>} />
        <Route path="admin/transactions" element={<PrivateRoute adminOnly><AdminTransactions /></PrivateRoute>} />
        <Route path="admin/reports" element={<PrivateRoute adminOnly><AdminReports /></PrivateRoute>} />
        <Route path="admin/settings" element={<PrivateRoute adminOnly><AdminSettings /></PrivateRoute>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
