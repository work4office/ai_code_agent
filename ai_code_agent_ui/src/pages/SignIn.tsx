import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function SignIn() {
  const { login } = useAuth();

  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: "", password: "" });

  const handleChange = (e: React.ChangeEvent) =>
    setFormData({
      ...formData,
      [(e.target as HTMLInputElement).name]: (e.target as HTMLInputElement)
        .value,
    });

  const handleSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();
    try {
      await login(formData);
      navigate("/");
    } catch (err) {
      alert("Authentication failed. Check your credentials.");
    }
  };

  return (
    <div className="flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-md space-y-6">
        <h2 className="text-3xl font-bold text-center">Sign in</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            placeholder="Email"
            required
            className="w-full border rounded px-3 py-2"
            onChange={handleChange}
          />
          <input
            type="password"
            name="password"
            placeholder="Password"
            required
            className="w-full border rounded px-3 py-2"
            onChange={handleChange}
          />
          <button
            type="submit"
            disabled={!formData.email || !formData.password}
            className={`cursor-pointer disabled:cursor-not-allowed w-full bg-[#0d0e12] disabled:opacity-50 disabled:hover:bg-[#0d0e12] text-white py-2 rounded-md hover:bg-[#0d0e12]`}
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
