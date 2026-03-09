import client from "./client";

const productsAPI = {
  list: (params = {}) =>
    client.get("/products/", { params }),

  getById: (id) =>
    client.get(`/products/${id}/`),

  getFeatured: () =>
    client.get("/products/featured/"),

  getSeasonal: (params = {}) =>
    client.get("/products/seasonal/", { params }),

  getByFarm: (farmSlug, params = {}) =>
    client.get(`/products/by-farm/${farmSlug}/`, { params }),

  create: (data) =>
    client.post("/products/", data),

  update: (id, data) =>
    client.patch(`/products/${id}/`, data),

  remove: (id) =>
    client.delete(`/products/${id}/`),

  // Categories
  getCategories: () =>
    client.get("/products/categories/"),

  getCategoryBySlug: (slug) =>
    client.get(`/products/categories/${slug}/`),

  // Reviews for a product
  getReviews: (productId) =>
    client.get("/reviews/", { params: { product: productId } }),

  getReviewStats: (productId) =>
    client.get("/reviews/stats/", { params: { product: productId } }),

  createReview: (data) =>
    client.post("/reviews/", data),
};

export default productsAPI;
