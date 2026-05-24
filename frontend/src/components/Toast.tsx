import React from 'react';

export interface ToastMessage {
  text: string;
  type: 'success' | 'error';
}

interface ToastProps {
  toast: ToastMessage | null;
}

export default function Toast({ toast }: ToastProps) {
  if (!toast) return null;

  return (
    <div className="fixed top-4 left-1/2 -translate-x-1/2 z-[100] animate-fade-in flex items-center gap-2 px-4 py-2.5 rounded-full shadow-lg border text-xs font-semibold backdrop-blur-md bg-surface-container-lowest border-primary/10">
      <span
        className={`w-2 h-2 rounded-full ${
          toast.type === 'success' ? 'bg-primary animate-ping' : 'bg-error animate-ping'
        }`}
      />
      <span className={toast.type === 'success' ? 'text-primary' : 'text-error'}>
        {toast.text}
      </span>
    </div>
  );
}