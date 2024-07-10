import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { ChakraProvider } from "@chakra-ui/react";
import AuthProvider from "react-auth-kit";
import RequireAuth from "@auth-kit/react-router/RequireAuth";
import createStore from "react-auth-kit/createStore";
import RegistrationForm from "./components/auth/RegistrationForm/RegistrationForm.tsx";
import LoginForm from "./components/auth/LoginForm/LoginForm.tsx";
import Home from "./components/Home/Home.tsx";
import "./App.css";
import { Toaster } from "react-hot-toast";

const store = createStore({
  authName: "_auth",
  authType: "cookie",
  cookieDomain: window.location.hostname,
  cookieSecure: window.location.protocol === "https:",
});

function App() {
  return (
    <AuthProvider store={store}>
      <ChakraProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Navigate replace to="/home" />} />
            <Route
              path="/home"
              element={
                <RequireAuth fallbackPath={"/login"}>
                  <Home />
                </RequireAuth>
              }
            />
            <Route path="/register" element={<RegistrationForm />} />
            <Route path="/login" element={<LoginForm />} />
          </Routes>
        </Router>
        <Toaster
          position="top-right"
          gutter={8}
          toastOptions={{ duration: 3000 }}
        />
      </ChakraProvider>
    </AuthProvider>
  );
}

export default App;
