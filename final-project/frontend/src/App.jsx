import { useState } from "react";
import RecipeForm from "./components/RecipeForm";
import RecipeCard from "./components/RecipeCard";
import { generateRecipe } from "./services/api";

function App() {
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async (formData) => {
    try {
      setLoading(true);

      const data = await generateRecipe(formData);
      setRecipe(data);

    } catch (err) {
      console.error("Error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>AI Recipe Generator</h1>

      <RecipeForm onGenerate={handleGenerate} />

      {loading && <p>Generating recipe...</p>}

      <RecipeCard recipe={recipe} />
    </div>
  );
}

export default App;