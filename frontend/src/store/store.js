import { configureStore } from "@reduxjs/toolkit";
import authReducer from "./authSlice";
import cartReducer from "./cartSlice";

export const store = configureStore({
  reducer: {
    auth: authReducer,
    cart: cartReducer,
  },
  devTools: process.env.NODE_ENV !== "production",
});
