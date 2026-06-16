import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactElement } from "react";

import { getToken } from "./api/client";
import AdminLayout from "./layouts/AdminLayout";
import Chat from "./pages/Chat";
import Conversations from "./pages/Conversations";
import Dashboard from "./pages/Dashboard";
import Knowledge from "./pages/Knowledge";
import Leads from "./pages/Leads";
import Login from "./pages/Login";

function RequireAuth({ children }: { children: ReactElement }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="knowledge" element={<Knowledge />} />
        <Route path="chat" element={<Chat />} />
        <Route path="conversations" element={<Conversations />} />
        <Route path="leads" element={<Leads />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
