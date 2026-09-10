import React, { useState } from "react";
import { Link2, Upload } from "lucide-react";
import { repositoryService } from "../api/repositoryService";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<"url" | "local" | "recent">("url");
  const [repoInput, setRepoInput] = useState("");
  const { user, isLoading } = useAuth();
  const { addToast } = useToast();

  const ingestGit = async () => {
    if (!user || isLoading) return;
    const res = await repositoryService.ingest_repo(repoInput);
    setRepoInput("");
    console.log(res);
    addToast(res.message, "info");
  };

  return (
    <div className="text-slate-100 font-sans">
      <main>
        <div className="max-w-5xl mx-auto p-8 space-y-8">
          <section className="shadow-sm ring-1 ring-inset ring-gray-300 p-6 rounded-xl">
            <h2 className="text-sm font-medium text-slate-400 mb-4">
              Start by ingesting the repository, or use an existing one from the
              left side.
            </h2>
            <div className="shadow-sm ring-1 ring-inset ring-gray-300 flex items-center gap-3 p-2 rounded-xl">
              <div className="shadow-sm ring-1 ring-inset ring-gray-300 flex items-center rounded-lg p-1">
                <button
                  onClick={() => setActiveTab("url")}
                  className={`p-2.5 rounded-md transition ${activeTab === "url" ? "bg-[#0d0e12] text-white shadow-md" : "text-slate-400 hover:text-slate-200"}`}
                >
                  <Link2 size={18} />
                </button>
                {/* <button
                                    onClick={() => setActiveTab("local")}
                                    className={`p-2.5 rounded-md transition ${activeTab === "local" ? "bg-[#0d0e12] text-white shadow-md" : "text-slate-400 hover:text-slate-200"}`}
                                >
                                    <Folder size={18} />
                                </button> */}
                {/* <button
                                    onClick={() => setActiveTab("recent")}
                                    className={`p-2.5 rounded-md transition ${activeTab === "recent" ? "bg-[#0d0e12] text-white shadow-md" : "text-slate-400 hover:text-slate-200"}`}
                                >
                                    <FolderPlus size={18} />
                                </button> */}
              </div>
              <div className="shadow-sm ring-1 ring-inset ring-gray-300 items-center rounded-lg p-1 flex-1">
                <input
                  type="text"
                  value={repoInput}
                  onChange={(e) => setRepoInput(e.target.value)}
                  placeholder={
                    activeTab === "url"
                      ? "GitHub repository URL"
                      : activeTab === "local"
                        ? "Enter absolute path to local repository directory"
                        : "Search previously parsed configurations..."
                  }
                  className="w-full bg-transparent text-slate-600 placeholder-slate-600 text-sm px-3 py-2 outline-none focus:placeholder-slate-500 transition"
                />
              </div>
              {/* Action Button */}
              <button
                onClick={ingestGit}
                title={!user ? "Log In to ingest" : "Ingest repository"}
                disabled={!user || isLoading || !repoInput}
                className={`cursor-pointer disabled:cursor-not-allowed bg-[#0d0e12] disabled:opacity-50 disabled:hover:bg-[#0d0e12] text-white px-5 py-2.5 rounded-lg font-medium text-sm flex items-center gap-2 transition active:scale-[0.98]`}
              >
                <span>Ingest</span>
                <Upload size={16} />
              </button>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
