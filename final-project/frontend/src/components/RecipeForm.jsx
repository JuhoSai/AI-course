import { useState } from "react";

export default function RecipeForm({ onGenerate }) {
  const [form, setForm] = useState({
    ingredients: "",
    cuisine: "",
    diet: "",
    time: 30
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = () => {
    onGenerate(form);
  };

  return (
    <div style={{ marginBottom: 20 }}>
      <h2>Enter ingredients</h2>

      <input
        name="ingredients"
        placeholder="e.g. chicken, rice"
        value={form.ingredients}
        onChange={handleChange}
      />

      <br />

      <input
        name="cuisine"
        placeholder="Cuisine"
        value={form.cuisine}
        onChange={handleChange}
      />

      <br />

      <input
        name="diet"
        placeholder="Diet"
        value={form.diet}
        onChange={handleChange}
      />

      <br />

      <input
        name="time"
        type="number"
        value={form.time}
        onChange={handleChange}
      />

      <br />

      <button onClick={handleSubmit}>
        Generate Recipe
      </button>
    </div>
  );
}