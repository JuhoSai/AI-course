import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:8000"
});

export const generateRecipe = async (data) => {
  const res = await API.post("/generate-recipe", data);
  return res.data;
};