import React, { useState } from "react";
import axios from "axios";

export default function QueryForm({ setResponse }) {
  const [query, setQuery] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await axios.post("http://localhost:8000/advisory/", new URLSearchParams({ query }));
    setResponse(res.data);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white shadow-lg p-4 rounded-lg flex gap-3">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a farming question..."
        className="flex-grow border p-2 rounded"
      />
      <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded">
        Ask
      </button>
    </form>
  );
}
