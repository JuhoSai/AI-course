export default function RecipeCard({ recipe }) {
  if (!recipe) return null;

  return (
    <div style={{ marginTop: 20 }}>
      <h2>{recipe.title}</h2>

      <h3>Ingredients</h3>
      <ul>
        {recipe.ingredients?.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>

      <h3>Steps</h3>
      <ol>
        {recipe.steps?.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>
    </div>
  );
}