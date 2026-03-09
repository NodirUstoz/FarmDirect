import React from "react";
import ReactDOM from "react-dom/client";
import { Provider } from "react-redux";
import { BrowserRouter } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import App from "./App";
import { store } from "./store/store";
import "./styles/global.css";

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <App />
        <ToastContainer
          position="bottom-right"
          autoClose={4000}
          hideProgressBar={false}
          closeOnClick
          pauseOnHover
        />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
);
