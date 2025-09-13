import { useAuth } from "./context/AuthContext";

export default function TestAuth() {
  const { user } = useAuth();
  return <div>Auth hook is working. User: {user ? user.email : "none"}</div>;
}
