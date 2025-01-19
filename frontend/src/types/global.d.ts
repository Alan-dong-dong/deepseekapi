export {}

declare global {
  interface Window {
    copyCode: (event: MouseEvent) => void;
  }
} 