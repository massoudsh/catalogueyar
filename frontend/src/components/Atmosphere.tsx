import type { ReactNode } from "react";

type AtmosphereProps = {
  children: ReactNode;
};

export function Atmosphere({ children }: AtmosphereProps) {
  return (
    <div className="atmosphere relative min-h-screen overflow-x-hidden text-ink">
      <div className="atmosphere-grid pointer-events-none absolute inset-0" aria-hidden />
      <div
        className="pointer-events-none absolute -left-24 top-24 h-72 w-72 rounded-full bg-teal/10 blur-3xl"
        aria-hidden
      />
      <div
        className="pointer-events-none absolute -right-16 bottom-10 h-80 w-80 rounded-full bg-saffron/20 blur-3xl"
        aria-hidden
      />
      <div className="relative z-10">{children}</div>
    </div>
  );
}
