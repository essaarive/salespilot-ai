import {
  Bot,
  Building2,
  Database,
  LayoutDashboard,
  LogOut,
  MessageSquareText,
  Settings,
  UsersRound,
} from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { clearToken } from "../api/client";

const navItems = [
  { path: "/dashboard", label: "仪表盘", icon: LayoutDashboard },
  { path: "/knowledge", label: "知识库管理", icon: Database },
  { path: "/ai-settings", label: "模型设置", icon: Settings },
  { path: "/company-settings", label: "企业设置", icon: Building2 },
  { path: "/chat", label: "AI 对话测试", icon: Bot },
  { path: "/conversations", label: "对话记录", icon: MessageSquareText },
  { path: "/leads", label: "客户线索", icon: UsersRound },
];

export default function AdminLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearToken();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="flex h-16 items-center border-b border-slate-100 px-6">
          <button
            className="-mx-2 flex w-full cursor-pointer items-center gap-3 rounded-md px-2 py-2 text-left transition hover:bg-slate-50 hover:opacity-90"
            type="button"
            onClick={() => navigate("/")}
            aria-label="返回官网首页"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-600 text-white">
              <Bot size={18} />
            </div>
            <div>
              <p className="text-lg font-semibold text-slate-950">SalesPilot AI</p>
              <p className="text-xs text-slate-500">智销助手</p>
            </div>
          </button>
        </div>
        <nav className="space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  [
                    "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition",
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
                  ].join(" ")
                }
              >
                <Icon size={18} />
                {item.label}
              </NavLink>
            );
          })}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 lg:px-8">
          <div>
            <h1 className="text-base font-semibold text-slate-950 lg:text-lg">智销助手管理后台</h1>
            <p className="hidden text-xs text-slate-500 sm:block">AI 销售客服 MVP 演示系统</p>
          </div>
          <div className="flex items-center gap-2">
            <nav className="flex gap-1 overflow-x-auto lg:hidden">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      [
                        "rounded-md p-2",
                        isActive ? "bg-brand-50 text-brand-700" : "text-slate-500",
                      ].join(" ")
                    }
                    title={item.label}
                    aria-label={item.label}
                  >
                    <Icon size={18} />
                  </NavLink>
                );
              })}
            </nav>
            <button className="btn-secondary" type="button" onClick={handleLogout}>
              <LogOut size={16} />
              <span className="hidden sm:inline">退出</span>
            </button>
          </div>
        </header>
        <main className="px-4 py-6 lg:px-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
