import { useState } from "react";
import RecipeForm from "./components/RecipeForm";
import RecipeCard from "./components/RecipeCard";
import { generateRecipe } from "./services/api";

function App() {
  // State for storing the generated recipe
  const [recipe, setRecipe] = useState(null);

  // State for tracking loading status during API call
  const [loading, setLoading] = useState(false);

  // Handles form submission and triggers recipe generation
  const handleGenerate = async (formData) => {
    try {
      setLoading(true);

      // Call backend API to generate recipe
      const data = await generateRecipe(formData);

      // Update state with received recipe
      setRecipe(data);
    } catch (err) {
      // Log errors for debugging
      console.error("Error:", err);
    } finally {
      // Ensure loading state is reset
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>AI Recipe Generator</h1>

      {/* Pass handler to form component */}
      <RecipeForm onGenerate={handleGenerate} />

      {/* Render loading indicator conditionally */}
      {loading && <p>Generating recipe...</p>}

      {/* Render recipe if available */}
      <RecipeCard recipe={recipe} />
    </div>
  );
}

export default App;