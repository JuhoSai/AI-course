import axios from "axios";

// Create a pre-configured Axios instance for backend communication
const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
});
// Sends a POST request to generate a recipe based on user input
export const generateRecipe = async (data) => {
  const res = await API.post("/generate-recipe", data);

    // Return only the response payload from the backend
  return res.data;
};