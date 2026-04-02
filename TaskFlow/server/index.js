// import cookieParser from "cookie-parser";
// import cors from "cors";
// import dotenv from "dotenv";
// import express from "express";
// import morgan from "morgan";
// import { errorHandler, routeNotFound } from "./middleware/errorMiddleware.js";
// import routes from "./routes/index.js";
// import dbConnection from "./utils/connectDB.js";

// dotenv.config();

// dbConnection();

// const port = process.env.PORT || 5000;
// const app = express();

// const allowedOrigins = [
//   process.env.CLIENT_ORIGIN || "http://localhost:3000",
//   "http://localhost:3001",
//   "https://mern-task-manager-app.netlify.app",
// ];

// app.use(
//   cors({
//     origin: function (origin, callback) {
//       // Allow requests with no origin (mobile apps, curl, etc.)
//       if (!origin) return callback(null, true);
//       if (allowedOrigins.includes(origin)) {
//         return callback(null, true);
//       }
//       return callback(new Error("Not allowed by CORS"));
//     },
//     methods: ["GET", "POST", "DELETE", "PUT", "PATCH"],
//     credentials: true,
//   })
// );

// app.use(express.json());
// app.use(express.urlencoded({ extended: true }));
// app.use(cookieParser());

// if (process.env.NODE_ENV === "development") {
//   app.use(morgan("dev"));
// }

// // Health check endpoint
// app.get("/health", (req, res) => {
//   res.status(200).json({ status: "ok", timestamp: new Date().toISOString() });
// });

// app.use("/api", routes);

// app.use(routeNotFound);
// app.use(errorHandler);

// // Only start the server if this file is run directly (not imported by tests)
// if (process.env.NODE_ENV !== "test") {
//   app.listen(port, () =>
//     console.log(`🚀 Server running on http://localhost:${port}`)
//   );
// }

// export default app;

import cookieParser from "cookie-parser";
import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import morgan from "morgan";
import { errorHandler, routeNotFound } from "./middleware/errorMiddleware.js";
import routes from "./routes/index.js";
import dbConnection from "./utils/connectDB.js";

dotenv.config();

// Only connect to real DB if NOT in test mode
if (process.env.NODE_ENV !== "test") {
  dbConnection();
}

const port = process.env.PORT || 5001;
const app = express();

const allowedOrigins = [
  process.env.CLIENT_ORIGIN || "http://localhost:3000",
  "http://localhost:3001",
  "https://mern-task-manager-app.netlify.app",
];

app.use(
  cors({
    origin: function (origin, callback) {
      if (!origin) return callback(null, true);
      if (allowedOrigins.includes(origin)) {
        return callback(null, true);
      }
      return callback(new Error("Not allowed by CORS"));
    },
    methods: ["GET", "POST", "DELETE", "PUT", "PATCH"],
    credentials: true,
  })
);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

if (process.env.NODE_ENV === "development") {
  app.use(morgan("dev"));
}

app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok", timestamp: new Date().toISOString() });
});

app.use("/api", routes);

app.use(routeNotFound);
app.use(errorHandler);

if (process.env.NODE_ENV !== "test") {
  app.listen(port, () =>
    console.log(`🚀 Server running on http://localhost:${port}`)
  );
}

export default app;