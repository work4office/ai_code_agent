import React, { useState } from "react";
import useApi from "../hooks/useApi";
import { useToast } from "../context/ToastContext";

export default function SignUp() {
  const { create_user } = useApi();
  const { addToast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });
  const handleChange = (e: any) =>
    setFormData({ ...formData, [e.target.name]: e.target.value });
  const handleSubmit = async (e: any) => {
    e.preventDefault();

    const res = await create_user({
      name: formData.name,
      email: formData.email,
      password: formData.password,
    });
    console.log(res);
    addToast("User created, Log In.", "success");
  };

  return (
    <div className="flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white p-8 rounded-xl shadow-md space-y-6">
        <h2 className="text-3xl font-bold text-center">Create account</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <input
            type="text"
            name="name"
            placeholder="Full Name"
            required
            className="w-full border rounded px-3 py-2"
            onChange={handleChange}
          />
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
            disabled={!formData.name || !formData.email || !formData.password}
            className="cursor-pointer disabled:cursor-not-allowed w-full bg-[#0d0e12] disabled:opacity-50 disabled:hover:bg-[#0d0e12] text-white py-2 rounded-md hover:bg-[#0d0e12]"
          >
            Sign Up
          </button>
        </form>
      </div>
    </div>
  );
}
