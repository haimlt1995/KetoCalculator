import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const defaultForm = {
  unit_system: "metric",
  sex: "male",
  age_years: 0,
  height_cm: 0,
  weight_kg: 0,
  activity_level: "sedentary",
  goal: "maintain",
};

const colors = {
  bg: "radial-gradient(circle at 20% 20%, rgba(56,189,248,0.12), rgba(14,165,233,0)), radial-gradient(circle at 80% 0%, rgba(94,234,212,0.18), rgba(14,165,233,0)), #0b1224",
  card: "rgba(15, 23, 42, 0.82)",
  border: "rgba(255, 255, 255, 0.08)",
  text: "#e2e8f0",
  textMuted: "#94a3b8",
  accent: "#22d3ee",
  accentBold: "#0ea5e9",
};

function Field({ label, hint, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: colors.text }}>{label}</span>
        {hint ? (
          <span style={{ fontSize: 12, color: colors.textMuted, lineHeight: 1.4 }}>{hint}</span>
        ) : null}
      </div>
      {children}
    </div>
  );
}

function Card({ title, subtitle, children }) {
  return (
    <div
      style={{
        border: `1px solid ${colors.border}`,
        borderRadius: 40,
        padding: 40,
        background: colors.card,
        boxShadow: "0 20px 60px rgba(0,0,0,0.28)",
        backdropFilter: "blur(8px)",
        color: colors.text,
      }}
    >
      <div style={{ marginBottom: 12 }}>
        <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: -0.2 }}>{title}</div>
        {subtitle ? (
          <div style={{ fontSize: 13, color: colors.textMuted, lineHeight: 1.5 }}>{subtitle}</div>
        ) : null}
      </div>
      {children}
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: "12px 14px",
  borderRadius: 12,
  border: `1px solid ${colors.border}`,
  outline: "none",
  fontSize: 14,
  background: "rgba(255,255,255,0.05)",
  color: colors.text,
  fontWeight: 600,
};

export default function App() {
  const [form, setForm] = useState(defaultForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [isNarrow, setIsNarrow] = useState(
    typeof window !== "undefined" ? window.innerWidth < 1040 : false
  );
  const twoCol = { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 };

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function onCalculate() {
    setError("");
    setResult(null);
    setLoading(true);

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
    } finally {
      setLoading(false);
    }
  }

  const chartData = useMemo(() => {
    return (
      result?.forecast?.map((p) => ({
        week: p.week,
        weight: p.weight_kg,
      })) ?? []
    );
  }, [result]);

  useEffect(() => {
    const handler = () => setIsNarrow(window.innerWidth < 1040);
    window.addEventListener("resize", handler);
    return () => window.removeEventListener("resize", handler);
  }, []);

  useEffect(() => {
    const prevBg = document.body.style.background;
    const prevMargin = document.body.style.margin;
    document.body.style.background = colors.bg;
    document.body.style.margin = "0";
    return () => {
      document.body.style.background = prevBg;
      document.body.style.margin = prevMargin;
    };
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: colors.bg,
        padding: "36px 20px 72px",
        boxSizing: "border-box",
        color: colors.text,
      }}
    >
      <div style={{ maxWidth: 1180, margin: "0 auto", display: "grid", gap: 16 }}>
        <div
          style={{
            padding: "18px 20px",
            borderRadius: 16,
            background: `linear-gradient(120deg, ${colors.accentBold}, ${colors.accent})`,
            color: "#0b1224",
            boxShadow: "0 20px 60px rgba(14,165,233,0.35)",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div>
              <div style={{ fontSize: 24, fontWeight: 900, letterSpacing: -0.5 }}>
                Keto Calculator
              </div>
              <div style={{ fontSize: 14, opacity: 0.85, marginTop: 4, lineHeight: 1.5 }}>
                Enter your details to get calories, macros, and a weekly weight projection with a
                clean, focused layout.
              </div>
            </div>
            <div
              style={{
                fontSize: 12,
                fontWeight: 800,
                padding: "8px 12px",
                borderRadius: 999,
                background: "rgba(255,255,255,0.85)",
                color: "#0f172a",
                display: "inline-flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <span style={{ width: 8, height: 8, borderRadius: 99, background: colors.accentBold }} />
              Designed for clarity
            </div>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: isNarrow ? "1fr" : "minmax(360px, 420px) minmax(0, 1fr)",
            gap: 18,
            alignItems: "start",
          }}
        >
          {/* LEFT: Inputs */}
          <Card
            title="Inputs"
            subtitle="All calculations use metric internally. Imperial is converted automatically."
          >
            <div style={{ display: "grid", gap: 14 }}>
              <div style={twoCol}>
                <Field label="Unit system">
                  <select
                    style={inputStyle}
                    value={form.unit_system}
                    onChange={(e) => update("unit_system", e.target.value)}
                  >
                    <option value="metric">Metric</option>
                    <option value="imperial">Imperial</option>
                  </select>
                </Field>

                <Field label="Goal" hint="Lose: ~20% deficit · Gain: ~20% surplus">
                  <select
                    style={inputStyle}
                    value={form.goal}
                    onChange={(e) => update("goal", e.target.value)}
                  >
                    <option value="lose">Lose</option>
                    <option value="maintain">Maintain</option>
                    <option value="gain">Gain</option>
                  </select>
                </Field>
              </div>

              <div style={twoCol}>
                <Field label="Sex">
                  <select
                    style={inputStyle}
                    value={form.sex}
                    onChange={(e) => update("sex", e.target.value)}
                  >
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                  </select>
                </Field>

                <Field label="Age (years)">
                  <input
                    style={inputStyle}
                    type="number"
                    min={1}
                    value={form.age_years}
                    onChange={(e) => update("age_years", Number(e.target.value))}
                  />
                </Field>
              </div>

              {form.unit_system === "metric" ? (
                <div style={twoCol}>
                  <Field label="Height (cm)">
                    <input
                      style={inputStyle}
                      type="number"
                      min={1}
                      value={form.height_cm}
                      onChange={(e) => update("height_cm", Number(e.target.value))}
                    />
                  </Field>

                  <Field label="Weight (kg)">
                    <input
                      style={inputStyle}
                      type="number"
                      min={1}
                      value={form.weight_kg}
                      onChange={(e) => update("weight_kg", Number(e.target.value))}
                    />
                  </Field>
                </div>
              ) : (
                <div style={twoCol}>
                  <Field label="Height (in)">
                    <input
                      style={inputStyle}
                      type="number"
                      min={1}
                      value={form.height_in ?? 70.87}
                      onChange={(e) => update("height_in", Number(e.target.value))}
                    />
                  </Field>

                  <Field label="Weight (lb)">
                    <input
                      style={inputStyle}
                      type="number"
                      min={1}
                      value={form.weight_lb ?? 176.37}
                      onChange={(e) => update("weight_lb", Number(e.target.value))}
                    />
                  </Field>
                </div>
              )}

              <Field label="Activity level">
                <select
                  style={inputStyle}
                  value={form.activity_level}
                  onChange={(e) => update("activity_level", e.target.value)}
                >
                  <option value="sedentary">Sedentary</option>
                  <option value="light">Light</option>
                  <option value="moderate">Moderate</option>
                  <option value="very">Very</option>
                  <option value="athlete">Athlete</option>
                </select>
              </Field>

              <button
                onClick={onCalculate}
                disabled={loading}
                style={{
                  marginTop: 4,
                  width: "100%",
                  padding: "14px 16px",
                  borderRadius: 14,
                  border: "1px solid rgba(255,255,255,0.18)",
                  background: loading
                    ? "linear-gradient(120deg, #0ea5e9, #22d3ee)"
                    : "linear-gradient(120deg, #22d3ee, #0ea5e9)",
                  color: "#0b1224",
                  fontSize: 15,
                  fontWeight: 800,
                  cursor: loading ? "not-allowed" : "pointer",
                  opacity: loading ? 0.7 : 1,
                  boxShadow: "0 16px 40px rgba(14,165,233,0.35)",
                  transition: "transform 120ms ease, box-shadow 120ms ease",
                }}
              >
                {loading ? "Calculating..." : "Calculate"}
              </button>

              <div style={{ fontSize: 12, color: colors.textMuted, lineHeight: 1.5 }}>
                Note: BMR is adult-only for now (entries under 18 will return an error).
              </div>
            </div>
          </Card>

          {/* RIGHT: Results */}
          <div style={{ display: "grid", gap: 16 }}>
            <Card title="Results" subtitle="Clear summary of the main outputs.">
              {error ? (
                <div
                  style={{
                    border: "1px solid rgba(248,113,113,0.3)",
                    background: "rgba(248,113,113,0.08)",
                    padding: 12,
                    borderRadius: 12,
                    color: "#fecdd3",
                    fontSize: 13,
                  }}
                >
                  {error}
                </div>
              ) : !result ? (
                <div style={{ fontSize: 14, color: colors.textMuted }}>
                  Click <b>Calculate</b> to see your results.
                </div>
              ) : (
                <div style={{ display: "grid", gap: 14 }}>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
                    <Stat label="BMI" value={result.bmi.toFixed(2)} />
                    <Stat label="BMR (kcal)" value={Math.round(result.bmr)} />
                    <Stat label="TDEE (kcal)" value={Math.round(result.tdee)} />
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 12 }}>
                    <Stat
                      label="Body fat % (approx)"
                      value={result.body_fat_percent_estimate?.toFixed(1) ?? "n/a"}
                    />
                    <Stat label="FFMI" value={result.ffmi?.toFixed(2) ?? "n/a"} />
                  </div>

                  <div
                    style={{
                      borderTop: `1px solid ${colors.border}`,
                      paddingTop: 12,
                      display: "grid",
                      gap: 10,
                    }}
                  >
                    <div style={{ fontSize: 16, fontWeight: 800 }}>Macros</div>

                    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                      <Stat label="Calories" value={Math.round(result.macros.calories_total)} />
                      <Stat label="Protein (g)" value={Math.round(result.macros.protein_g)} />
                      <Stat label="Fat (g)" value={Math.round(result.macros.fat_g)} />
                      <Stat label="Net carbs (g)" value={Math.round(result.macros.net_carbs_g)} />
                    </div>
                  </div>
                </div>
              )}
            </Card>

            <Card title="Weight forecast" subtitle="Weekly projection based on your calorie target.">
              {result && chartData.length > 0 ? (
                <>
                  <div style={{ width: "100%", height: 280 }}>
                    <ResponsiveContainer>
                      <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                        <XAxis
                          dataKey="week"
                          tick={{ fill: colors.textMuted, fontSize: 12 }}
                          label={{
                            value: "Weeks",
                            position: "insideBottom",
                            offset: -5,
                            fill: colors.textMuted,
                          }}
                        />
                        <YAxis
                          domain={["auto", "auto"]}
                          tick={{ fill: colors.textMuted, fontSize: 12 }}
                          label={{
                            value: "Weight (kg)",
                            angle: -90,
                            position: "insideLeft",
                            fill: colors.textMuted,
                          }}
                        />
                        <Tooltip
                          contentStyle={{
                            background: "rgba(15,23,42,0.9)",
                            border: `1px solid ${colors.border}`,
                            borderRadius: 10,
                            color: colors.text,
                          }}
                          labelStyle={{ color: colors.textMuted }}
                        />
                        <Line
                          type="monotone"
                          dataKey="weight"
                          dot={false}
                          stroke={colors.accent}
                          strokeWidth={3}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div style={{ fontSize: 12, color: colors.textMuted, lineHeight: 1.4 }}>
                    Projection shows estimated <b>weekly</b> weight change based on calorie target.
                    Real results vary (water weight, metabolism, adherence).
                  </div>
                </>
              ) : (
                <div style={{ fontSize: 14, color: colors.textMuted }}>
                  Click <b>Calculate</b> to generate the forecast chart.
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

function Stat({ label, value }) {
  return (
    <div
      style={{
        border: `1px solid ${colors.border}`,
        borderRadius: 12,
        padding: 12,
        background: "rgba(255,255,255,0.03)",
      }}
    >
      <div style={{ fontSize: 12, color: colors.textMuted }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 900, marginTop: 6, color: colors.text }}>{value}</div>
    </div>
  );
}
