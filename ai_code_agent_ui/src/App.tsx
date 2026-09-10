import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import { AuthProvider } from "./context/AuthContext";
import { CommonProvider } from "./context/CommonContext";
import { ToastProvider } from "./context/ToastContext";
function App() {
  return (
    <AuthProvider>
      <CommonProvider>
        <ToastProvider>
          <RouterProvider router={router} />
        </ToastProvider>
      </CommonProvider>
    </AuthProvider>
  );
}

export default App;
