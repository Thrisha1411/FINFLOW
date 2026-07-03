import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom";
import "./styles.css";
import AppShell from "./ui/AppShell";
import { Dashboard } from "./views/Dashboard";
import { Transactions } from "./views/Transactions";
import { FraudCenter } from "./views/FraudCenter";
import { AiInsights } from "./views/AiInsights";
import { Subscriptions } from "./views/Subscriptions";
import { Budgets } from "./views/Budgets";
import { AuditLogs } from "./views/AuditLogs";
import { Settings } from "./views/Settings";
import { Login } from "./views/Login";
import { Register } from "./views/Register";

const queryClient = new QueryClient();
const router = createBrowserRouter([
  { path: "/login", element: <Login /> },
  { path: "/register", element: <Register /> },
  {
    path: "/",
    element: <AppShell />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <Dashboard /> },
      { path: "transactions", element: <Transactions /> },
      { path: "fraud", element: <FraudCenter /> },
      { path: "insights", element: <AiInsights /> },
      { path: "subscriptions", element: <Subscriptions /> },
      { path: "budgets", element: <Budgets /> },
      { path: "audit", element: <AuditLogs /> },
      { path: "settings", element: <Settings /> }
    ]
  }
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>
  </React.StrictMode>
);

