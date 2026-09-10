import React, {
    useState,
    useRef,
    type DragEvent,
    type ChangeEvent,
} from "react";
// import JSZip from "jszip";

interface FileItem {
    path: string;
    file: File;
}

export default function ZipUploader() {
    const [files, setFiles] = useState<FileItem[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [isZipping, setIsZipping] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Helper to process Drag and Drop entries recursively
    const traverseFileTree = async (item: any, path = "") => {
        const fileItems: FileItem[] = [];

        if (item.isFile) {
            const file = await new Promise<File>((resolve) => item.file(resolve));
            fileItems.push({ path: path + file.name, file });
        } else if (item.isDirectory) {
            const dirReader = item.createReader();
            const entries = await new Promise<any[]>((resolve) => {
                dirReader.readEntries(resolve);
            });
            for (const entry of entries) {
                const childItems = await traverseFileTree(
                    entry,
                    path + item.name + "/",
                );
                fileItems.push(...childItems);
            }
        }
        return fileItems;
    };

    // Handle Drag Events
    const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = async (e: DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        setIsDragging(false);

        const items = e.dataTransfer.items;
        if (!items) return;

        const allFileItems: FileItem[] = [];
        for (let i = 0; i < items.length; i++) {
            const item = items[i].webkitGetAsEntry();
            if (item) {
                const fileItems = await traverseFileTree(item);
                allFileItems.push(...fileItems);
            }
        }
        setFiles(allFileItems);
    };

    // Handle File Input Click Selection
    const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files) return;

        const fileList = Array.from(e.target.files);
        const fileItems: FileItem[] = fileList.map((file) => {
            // webkitRelativePath preserves folder structure during file dialog selection
            const path = file.webkitRelativePath || file.name;
            return { path, file };
        });

        setFiles(fileItems);
    };

    // Trigger file input click
    const triggerFileInput = () => {
        fileInputRef.current?.click();
    };

    // Generate and Download Zip
    const generateZip = async () => {
        if (files.length === 0) return;
        setIsZipping(true);

        try {
            //const zip = new JSZip();

            // Add each file to the zip archive matching its folder structure
            // files.forEach(({ path, file }) => {
            //     //zip.file(path, file);
            // });

            // Generate the blob
            // const content = await zip.generateAsync({ type: "blob" });

            // Trigger browser download
            //const url = URL.createObjectURL(content);
            const link = document.createElement("a");
            //link.href = url;
            link.download = `archive-${Date.now()}.zip`;
            document.body.appendChild(link);
            link.click();

            // Cleanup
            document.body.removeChild(link);
            //URL.revokeObjectURL(url);
        } catch (error) {
            console.error("Error creating zip archive:", error);
        } finally {
            setIsZipping(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-md border border-gray-100 mt-10">
            {/* Hidden input to handle folder selection click */}
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                // TypeScript quirk: requires type assertion or standard HTML props bypass for non-standard attributes
                {...({
                    webkitdirectory: "",
                    directory: "",
                    multiple: true,
                } as any)}
            />

            {/* Drop Zone Container */}
            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={triggerFileInput}
                className={`flex flex-col items-center justify-center border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors duration-200 ${isDragging
                        ? "border-indigo-500 bg-indigo-50"
                        : "border-gray-300 hover:border-indigo-400 hover:bg-gray-50"
                    }`}
            >
                <svg
                    className={`w-12 h-12 mb-4 transition-colors ${isDragging ? "text-indigo-500" : "text-gray-400"}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    xmlns="http://w3.org"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 19a2 2 0 01-2-2V7a2 2 0 012-2h4l2 2h4a2 2 0 012 2v1M5 19h14a2 2 0 002-2v-5a2 2 0 00-2-2H9l-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                </svg>
                <p className="mb-2 text-sm text-gray-500 font-medium">
                    <span className="text-indigo-600 font-semibold">
                        Click to upload folder
                    </span>{" "}
                    or drag and drop it here
                </p>
                <p className="text-xs text-gray-400">
                    All nested files and structures are automatically mapped
                </p>
            </div>

            {/* Selected Files & Zip Status UI */}
            {files.length > 0 && (
                <div className="mt-6 border-t border-gray-100 pt-4">
                    <div className="flex items-center justify-between mb-4">
                        <span className="text-sm font-medium text-gray-700">
                            Detected{" "}
                            <span className="font-semibold text-indigo-600">
                                {files.length}
                            </span>{" "}
                            file(s) inside folder structure
                        </span>
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                setFiles([]);
                            }}
                            className="text-xs text-red-500 hover:underline"
                        >
                            Clear
                        </button>
                    </div>

                    {/* Action Button */}
                    <button
                        onClick={generateZip}
                        disabled={isZipping}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2.5 px-4 rounded-lg transition-colors shadow disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        {isZipping ? (
                            <>
                                <svg
                                    className="animate-spin h-5 w-5 text-white"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                >
                                    <circle
                                        className="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        strokeWidth="4"
                                    />
                                    <path
                                        className="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                    />
                                </svg>
                                Compressing into ZIP...
                            </>
                        ) : (
                            "Download Folder as ZIP"
                        )}
                    </button>
                </div>
            )}
        </div>
    );
}
