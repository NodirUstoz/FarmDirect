import client from "./client";

const farmsAPI = {
  list: (params = {}) =>
    client.get("/farms/", { params }),

  getBySlug: (slug) =>
    client.get(`/farms/${slug}/`),

  create: (data) =>
    client.post("/farms/", data),

  update: (slug, data) =>
    client.patch(`/farms/${slug}/`, data),

  remove: (slug) =>
    client.delete(`/farms/${slug}/`),

  getHarvestCalendar: (slug) =>
    client.get(`/farms/${slug}/harvest_calendar/`),

  getCertifications: (slug) =>
    client.get(`/farms/${slug}/certifications/`),

  getPhotos: (slug) =>
    client.get(`/farms/${slug}/photos/`),

  // Reviews for a farm
  getReviews: (farmId) =>
    client.get("/reviews/", { params: { farm: farmId } }),

  getReviewStats: (farmId) =>
    client.get("/reviews/stats/", { params: { farm: farmId } }),
};

export default farmsAPI;
