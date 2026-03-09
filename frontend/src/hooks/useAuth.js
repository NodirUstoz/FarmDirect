import { useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { fetchProfile, logout } from "../store/authSlice";

/**
 * Custom hook that exposes auth state and helpers.
 *
 * Usage:
 *   const { user, isAuthenticated, isFarmer, loading, doLogout } = useAuth();
 */
export default function useAuth() {
  const dispatch = useDispatch();
  const { user, isAuthenticated, loading, error, accessToken } = useSelector(
    (state) => state.auth
  );

  // Fetch the user profile once when we have a token but no user object
  useEffect(() => {
    if (isAuthenticated && !user && !loading) {
      dispatch(fetchProfile());
    }
  }, [isAuthenticated, user, loading, dispatch]);

  const doLogout = () => {
    dispatch(logout());
  };

  return {
    user,
    isAuthenticated,
    loading,
    error,
    accessToken,
    isFarmer: user?.role === "farmer",
    isConsumer: user?.role === "consumer",
    doLogout,
  };
}
