import { Navigate, Route, Routes } from "react-router-dom";
import type { ReactElement } from "react";

import { getToken } from "./api/client";
import AdminLayout from "./layouts/AdminLayout";
import AISettings from "./pages/AISettings";
import Chat from "./pages/Chat";
import CompanySettings from "./pages/CompanySettings";
import Conversations from "./pages/Conversations";
import Dashboard from "./pages/Dashboard";
import Knowledge from "./pages/Knowledge";
import Leads from "./pages/Leads";
import Login from "./pages/Login";
import PublicChat from "./pages/PublicChat";
import PublicHome from "./pages/PublicHome";

function RequireAuth({ children }: { children: ReactElement }) {
  return getToken() ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<PublicHome />} />
      <Route path="/public-chat" element={<PublicChat />} />
      <Route path="/login" element={<Login />} />
      <Route
        element={
          <RequireAuth>
            <AdminLayout />
          </RequireAuth>
        }
      >
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="knowledge" element={<Knowledge />} />
        <Route path="ai-settings" element={<AISettings />} />
        <Route path="company-settings" element={<CompanySettings />} />
        <Route path="chat" element={<Chat />} />
        <Route path="conversations" element={<Conversations />} />
        <Route path="leads" element={<Leads />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
