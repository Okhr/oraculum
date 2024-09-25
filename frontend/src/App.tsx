import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import { ChakraProvider, extendTheme } from "@chakra-ui/react";
import AuthProvider from "react-auth-kit";
import { QueryClientProvider, QueryClient } from '@tanstack/react-query';
import RequireAuth from "@auth-kit/react-router/RequireAuth";
import createStore from "react-auth-kit/createStore";
import RegistrationForm from "./components/auth/RegistrationForm.tsx";
import LoginForm from "./components/auth/LoginForm.tsx";
import "./App.css";
import { Toaster } from "react-hot-toast";
import Library from "./components/pages/Library.tsx";
import Entities from "./components/pages/Entities.tsx";

const store = createStore({
  authName: "_auth",
  authType: "cookie",
  cookieDomain: window.location.hostname,
  cookieSecure: window.location.protocol === "https:",
});

const theme = extendTheme({
  colors: {
    tangerine: {
      "50": "#FFF4E5",
      "100": "#FFDFB8",
      "200": "#FFCA8A",
      "300": "#FFB55C",
      "400": "#FFA12E",
      "500": "#FF8C00",
      "600": "#CC7000",
      "700": "#995400",
      "800": "#663800",
      "900": "#331C00"
    },
    indigo: {
      "50": "#ECE9FC",
      "100": "#CBC1F6",
      "200": "#A999EF",
      "300": "#8771E9",
      "400": "#654AE3",
      "500": "#4422DD",
      "600": "#361BB1",
      "700": "#291485",
      "800": "#1B0E58",
      "900": "#0E072C"
    },
    emerald: {
      "50": "#ECF9F0",
      "100": "#C9EED5",
      "200": "#A6E3BA",
      "300": "#83D89F",
      "400": "#60CD84",
      "500": "#3DC269",
      "600": "#319B54",
      "700": "#25743F",
      "800": "#184E2A",
      "900": "#0C2715"
    },
    violet: {
      "50": "#F5EEF6",
      "100": "#E2D0E6",
      "200": "#CFB2D6",
      "300": "#BC94C7",
      "400": "#A976B7",
      "500": "#9758A7",
      "600": "#784785",
      "700": "#5A3564",
      "800": "#3C2343",
      "900": "#1E1221"
    },
  },
})


const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider store={store}>
        <ChakraProvider theme={theme}>
          <Router>
            <Routes>
              <Route path="/" element={<Navigate replace to="/library" />} />
              <Route
                path="/library"
                element={
                  <RequireAuth fallbackPath={"/login"}>
                    <Library />
                  </RequireAuth>
                }
              />
              <Route
                path="/entities"
                element={
                  <RequireAuth fallbackPath={"/login"}>
                    <Entities />
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
    </QueryClientProvider>
  );
}

export default App;
