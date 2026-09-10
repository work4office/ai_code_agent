export function isNullOrUndefined(data: any | undefined) {
  return data === undefined || data === null;
}

export const getInitials = (name: string) => {
  if (!name) return "";

  const parts = name.trim().split(/\s+/);
  const firstLetter = parts[0] ? parts[0].charAt(0).toUpperCase() : "";
  const lastLetter =
    parts.length > 1 ? parts[parts.length - 1].charAt(0).toUpperCase() : "";

  return `${firstLetter}${lastLetter}`;
};

const EXTENSION_TO_LANGUAGE_MAP: Record<string, string> = {
  js: "javascript",
  jsx: "javascriptreact",
  ts: "typescript",
  tsx: "typescriptreact",
  html: "html",
  css: "css",
  json: "json",
  md: "markdown",
  py: "python",
  rs: "rust",
  go: "go",
  txt: "text",
};

export function getLanguageByFilename(filename: string): string {
  // Extract extension after the last dot, fallback to lowercase
  const ext = filename.split(".").pop()?.toLowerCase();

  if (!ext || !EXTENSION_TO_LANGUAGE_MAP[ext]) {
    return "unknown";
  }

  return EXTENSION_TO_LANGUAGE_MAP[ext];
}

export const getLanguage = (activeFilePath: string) => {
  let lang = "javascript";
  const fileName = activeFilePath?.split("/").pop();
  if (fileName) {
    lang = getLanguageByFilename(fileName);
  }
  return lang;
};
