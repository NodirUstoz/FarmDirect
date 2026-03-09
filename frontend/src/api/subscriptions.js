import client from "./client";

const subscriptionsAPI = {
  // Plans
  listPlans: () =>
    client.get("/subscriptions/plans/"),

  getPlan: (slug) =>
    client.get(`/subscriptions/plans/${slug}/`),

  // Boxes (authenticated)
  listBoxes: () =>
    client.get("/subscriptions/boxes/"),

  getBox: (id) =>
    client.get(`/subscriptions/boxes/${id}/`),

  createBox: (data) =>
    client.post("/subscriptions/boxes/", data),

  updateBox: (id, data) =>
    client.patch(`/subscriptions/boxes/${id}/`, data),

  pauseBox: (id) =>
    client.post(`/subscriptions/boxes/${id}/pause/`),

  resumeBox: (id) =>
    client.post(`/subscriptions/boxes/${id}/resume/`),

  cancelBox: (id) =>
    client.post(`/subscriptions/boxes/${id}/cancel/`),

  getBoxOrders: (id) =>
    client.get(`/subscriptions/boxes/${id}/orders/`),

  skipNext: (id) =>
    client.post(`/subscriptions/boxes/${id}/skip-next/`),
};

export default subscriptionsAPI;
