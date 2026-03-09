import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import authAPI from "../api/auth";

// ---------------------------------------------------------------------------
// Helpers -- persist tokens in localStorage
// ---------------------------------------------------------------------------
const loadTokens = () => {
  try {
    return {
      accessToken: localStorage.getItem("accessToken") || null,
      refreshToken: localStorage.getItem("refreshToken") || null,
    };
  } catch {
    return { accessToken: null, refreshToken: null };
  }
};

const persistTokens = (access, refresh) => {
  localStorage.setItem("accessToken", access);
  localStorage.setItem("refreshToken", refresh);
};

const clearTokens = () => {
  localStorage.removeItem("accessToken");
  localStorage.removeItem("refreshToken");
};

// ---------------------------------------------------------------------------
// Async thunks
// ---------------------------------------------------------------------------
export const loginUser = createAsyncThunk(
  "auth/login",
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const { data } = await authAPI.login(email, password);
      persistTokens(data.access, data.refresh);
      return data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.message || "Login failed."
      );
    }
  }
);

export const registerUser = createAsyncThunk(
  "auth/register",
  async (userData, { rejectWithValue }) => {
    try {
      const { data } = await authAPI.register(userData);
      persistTokens(data.tokens.access, data.tokens.refresh);
      return data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.message || "Registration failed."
      );
    }
  }
);

export const fetchProfile = createAsyncThunk(
  "auth/fetchProfile",
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await authAPI.getProfile();
      return data;
    } catch (err) {
      return rejectWithValue(
        err.response?.data?.message || "Failed to load profile."
      );
    }
  }
);

// ---------------------------------------------------------------------------
// Slice
// ---------------------------------------------------------------------------
const savedTokens = loadTokens();

const authSlice = createSlice({
  name: "auth",
  initialState: {
    user: null,
    accessToken: savedTokens.accessToken,
    refreshToken: savedTokens.refreshToken,
    isAuthenticated: !!savedTokens.accessToken,
    loading: false,
    error: null,
  },
  reducers: {
    logout(state) {
      state.user = null;
      state.accessToken = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      clearTokens();
    },
    setTokens(state, action) {
      const { access, refresh } = action.payload;
      state.accessToken = access;
      state.refreshToken = refresh;
      state.isAuthenticated = true;
      persistTokens(access, refresh);
    },
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false;
        state.accessToken = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.isAuthenticated = true;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.accessToken = action.payload.tokens.access;
        state.refreshToken = action.payload.tokens.refresh;
        state.isAuthenticated = true;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });

    // Fetch profile
    builder
      .addCase(fetchProfile.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { logout, setTokens, clearError } = authSlice.actions;
export default authSlice.reducer;
