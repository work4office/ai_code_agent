import {
  createBrowserRouter,
  createRoutesFromElements,
  Route,
} from "react-router-dom";
import Dashboard from "../components/Dashboard";
import NotFound from "../pages/NotFound";
import SignIn from "../pages/SignIn";
import SignUp from "../pages/SignUp";
import { ProtectedRoute } from "../components/ProtectedRoute";
import DashboardHome from "../pages/DashboardHome";
import CodeEditor from "../components/CodeEditor";

export const router = createBrowserRouter(
  createRoutesFromElements(
    <>
      <Route path="/" element={<Dashboard />}>
        <Route index element={<DashboardHome />} />
        <Route path="signIn" element={<SignIn />} />
        <Route path="signUp" element={<SignUp />} />
        <Route path="editor" element={<CodeEditor />} />

        {/* Protected or token-persisted routes */}
        <Route element={<ProtectedRoute />}>
          {/* <Route path="/dashboard" element={<Dashboard />} /> */}
        </Route>
        <Route path="*" element={<NotFound />} />
      </Route>
    </>,
  ),
);
