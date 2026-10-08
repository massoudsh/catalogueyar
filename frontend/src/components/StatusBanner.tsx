type StatusBannerProps = {
  message: string;
  tone?: "neutral" | "ok" | "error" | "warn";
};

const toneClass: Record<NonNullable<StatusBannerProps["tone"]>, string> = {
  neutral: "bg-ink/5 text-ink-soft",
  ok: "bg-ok/10 text-ok",
  error: "bg-danger/10 text-danger",
  warn: "bg-warn/10 text-warn",
};

export function StatusBanner({ message, tone = "neutral" }: StatusBannerProps) {
  return (
    <p className={`rounded-xl px-4 py-3 text-sm leading-7 ${toneClass[tone]}`} role="status">
      {message}
    </p>
  );
}
