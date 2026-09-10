import React, { useState, useRef, useEffect } from "react";
import { useCommonContext } from "../context/CommonContext";
import useApi from "../hooks/useApi";
import { Modal } from "../components/Modal";
import MultiFileDiffEditor from "./MultiFileDiffEditor";
import type { CodeChanges } from "../types/chat.types";

interface Message {
  id: string;
  sender: "user" | "ai";
  text: string;
}

export default function AIChatBot() {
  const { chat } = useApi();
  const { activeProject } = useCommonContext();
  const [messages, setMessages] = useState<Message[]>([
    { id: "1", sender: "ai", text: "Hello! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(true);
  const [chatResponse, setChatResponse] = useState<CodeChanges[] | undefined>(
    [],
  );
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.SubmitEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    setChatResponse([]);
    const response = await chat(userMessage.text, activeProject);
    setChatResponse(response?.changes);
    setIsModalOpen(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: response?.message ?? "",
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(false);
    }, 1000);
  };

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    // Reset height to recalculate correctly when text is deleted
    textarea.style.height = "auto";

    // Set height to scrollHeight (plus border borders if applicable)
    // We cap the max height at 160px (approx 5-6 lines) via Tailwind max-h-40
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }, [input]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // If user presses Enter without Shift, handle message submission
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (input.trim()) {
        console.log("Submitting:", input);
        setInput(""); // Clear input after submit
      }
    }
    // Shift + Enter naturally creates a new line, triggering the useEffect resize
  };

  return (
    <>
      <div className="flex flex-col h-full w-full ml-auto bg-white border border-[#ccc] shadow-sm ring-inset ring-gray-300 p-1 rounded-xl">
        {/* Header */}
        <div className="px-6 py-1 border-b border-gray-100 flex items-center justify-between bg-white">
          <h1 className="text-lg font-semibold text-gray-800">AI Assistant</h1>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-white">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                  msg.sender === "user"
                    ? "bg-black text-white rounded-br-none"
                    : "bg-gray-100 text-gray-800 rounded-bl-none"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 text-gray-500 px-4 py-3 rounded-2xl rounded-bl-none text-sm animate-pulse">
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form
          onSubmit={handleSend}
          className="p-4 border-t border-gray-100 bg-white"
        >
          <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-full px-4 py-2 focus-within:border-black transition-colors">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type a message..."
              rows={1}
              className="flex-1 bg-transparent border-none outline-none text-sm text-gray-800 placeholder-gray-400 resize-none py-2 max-h-40 overflow-y-auto"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="cursor-pointer bg-black text-white px-4 py-1.5 rounded-full text-sm font-medium hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            >
              Send
            </button>
          </div>
        </form>
      </div>
      {chatResponse && chatResponse?.length > 0 && (
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Review changes"
        >
          <MultiFileDiffEditor changes={chatResponse} />
        </Modal>
      )}
    </>
  );
}
