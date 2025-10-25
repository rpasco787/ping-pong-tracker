export async function getHealth() {
    const res = await fetch("http://localhost:8000/healthz");
    if (!res.ok) throw new Error("API Error");
    return res.json();
  }