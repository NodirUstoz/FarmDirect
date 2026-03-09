import client from "./client";

const authAPI = {
  login: (email, password) =>
    client.post("/auth/login/", { email, password }),

  register: (userData) =>
    client.post("/auth/register/", userData),

  refreshToken: (refreshToken) =>
    client.post("/auth/token/refresh/", { refresh: refreshToken }),

  logout: (refreshToken) =>
    client.post("/auth/logout/", { refresh: refreshToken }),

  getProfile: () =>
    client.get("/auth/profile/"),

  updateProfile: (data) =>
    client.patch("/auth/profile/", data),

  getFarmerProfile: () =>
    client.get("/auth/profile/farmer/"),

  updateFarmerProfile: (data) =>
    client.patch("/auth/profile/farmer/", data),

  getConsumerProfile: () =>
    client.get("/auth/profile/consumer/"),

  updateConsumerProfile: (data) =>
    client.patch("/auth/profile/consumer/", data),

  changePassword: (data) =>
    client.post("/auth/change-password/", data),
};

export default authAPI;
