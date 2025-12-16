import { useState } from "react";

const defaultForm = {
  unit_system: "metric",
  sex: "male",
  age_years: 25,
  height_cm: 180,
  weight_kg: 80,
  activity_level: "moderate",
  goal: "maintain",
};

export default function App() {
  const [form, setForm] = useState(defaultForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function onCalculate() {
    setError("");
    setResult(null);

    try {
      const res = await fetch("/api/calc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");

      setResult(data);
    } catch (e) {
      setError(e?.message || "Unknown error");
    }
  }

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 16, padding: 16 }}>
      <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
        <h2>Results</h2>
        {error && <p style={{ color: "crimson" }}>{error}</p>}
        {!error && !result && <p>Click Calculate.</p>}

        {result && (
          <div style={{ lineHeight: 1.8 }}>
            <div><b>BMI:</b> {result.bmi.toFixed(2)}</div>
            <div><b>BMR:</b> {Math.round(result.bmr)} kcal</div>
            <div><b>TDEE:</b> {Math.round(result.tdee)} kcal</div>
            <div><b>Body fat % (approx):</b> {result.body_fat_percent_estimate?.toFixed(1) ?? "n/a"}</div>
            <div><b>FFMI:</b> {result.ffmi?.toFixed(2) ?? "n/a"}</div>

            <h3 style={{ marginTop: 16 }}>Macros</h3>
            <div><b>Calories:</b> {Math.round(result.macros.calories_total)}</div>
            <div><b>Protein:</b> {Math.round(result.macros.protein_g)} g</div>
            <div><b>Fat:</b> {Math.round(result.macros.fat_g)} g</div>
            <div><b>Net carbs:</b> {Math.round(result.macros.net_carbs_g)} g</div>
          </div>
        )}
      </div>

      <div style={{ border: "1px solid #ddd", borderRadius: 12, padding: 16 }}>
        <h2>Inputs</h2>

        <label>Unit system</label>
        <select value={form.unit_system} onChange={(e) => update("unit_system", e.target.value)}>
          <option value="metric">metric</option>
          <option value="imperial">imperial</option>
        </select>

        <label>Sex</label>
        <select value={form.sex} onChange={(e) => update("sex", e.target.value)}>
          <option value="male">male</option>
          <option value="female">female</option>
        </select>

        <label>Age</label>
        <input type="number" value={form.age_years} onChange={(e) => update("age_years", Number(e.target.value))} />

        {form.unit_system === "metric" ? (
          <>
            <label>Height (cm)</label>
            <input type="number" value={form.height_cm} onChange={(e) => update("height_cm", Number(e.target.value))} />

            <label>Weight (kg)</label>
            <input type="number" value={form.weight_kg} onChange={(e) => update("weight_kg", Number(e.target.value))} />
          </>
        ) : (
          <>
            <label>Height (in)</label>
            <input
              type="number"
              value={form.height_in ?? 70.87}
              onChange={(e) => update("height_in", Number(e.target.value))}
            />

            <label>Weight (lb)</label>
            <input
              type="number"
              value={form.weight_lb ?? 176.37}
              onChange={(e) => update("weight_lb", Number(e.target.value))}
            />
          </>
        )}

        <label>Activity</label>
        <select value={form.activity_level} onChange={(e) => update("activity_level", e.target.value)}>
          <option value="sedentary">sedentary</option>
          <option value="light">light</option>
          <option value="moderate">moderate</option>
          <option value="very">very</option>
          <option value="athlete">athlete</option>
        </select>

        <label>Goal</label>
        <select value={form.goal} onChange={(e) => update("goal", e.target.value)}>
          <option value="lose">lose</option>
          <option value="maintain">maintain</option>
          <option value="gain">gain</option>
        </select>

        <button style={{ marginTop: 12 }} onClick={onCalculate}>
          Calculate
        </button>

        <p style={{ marginTop: 12, fontSize: 12, opacity: 0.8 }}>
          Note: BMR is adult-only for now (&lt;18 will return an error).
        </p>
      </div>
    </div>
  );
}
