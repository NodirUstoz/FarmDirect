import { createSlice } from "@reduxjs/toolkit";

// ---------------------------------------------------------------------------
// Persist cart in localStorage
// ---------------------------------------------------------------------------
const loadCart = () => {
  try {
    const raw = localStorage.getItem("cart");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
};

const persistCart = (items) => {
  localStorage.setItem("cart", JSON.stringify(items));
};

// ---------------------------------------------------------------------------
// Slice
// ---------------------------------------------------------------------------
const cartSlice = createSlice({
  name: "cart",
  initialState: {
    items: loadCart(),
  },
  reducers: {
    addToCart(state, action) {
      const { product, quantity = 1 } = action.payload;
      const existing = state.items.find((item) => item.product.id === product.id);

      if (existing) {
        existing.quantity += quantity;
      } else {
        state.items.push({ product, quantity });
      }
      persistCart(state.items);
    },

    removeFromCart(state, action) {
      const productId = action.payload;
      state.items = state.items.filter((item) => item.product.id !== productId);
      persistCart(state.items);
    },

    updateQuantity(state, action) {
      const { productId, quantity } = action.payload;
      const item = state.items.find((i) => i.product.id === productId);
      if (item) {
        if (quantity <= 0) {
          state.items = state.items.filter((i) => i.product.id !== productId);
        } else {
          item.quantity = quantity;
        }
      }
      persistCart(state.items);
    },

    clearCart(state) {
      state.items = [];
      persistCart([]);
    },
  },
});

// ---------------------------------------------------------------------------
// Selectors
// ---------------------------------------------------------------------------
export const selectCartItems = (state) => state.cart.items;

export const selectCartItemCount = (state) =>
  state.cart.items.reduce((total, item) => total + item.quantity, 0);

export const selectCartSubtotal = (state) =>
  state.cart.items.reduce(
    (total, item) => total + parseFloat(item.product.price) * item.quantity,
    0
  );

export const { addToCart, removeFromCart, updateQuantity, clearCart } = cartSlice.actions;
export default cartSlice.reducer;
