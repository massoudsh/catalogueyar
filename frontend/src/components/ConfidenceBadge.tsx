import { LOW_CONFIDENCE } from "../lib/config";

type ConfidenceBadgeProps = {
  value: number;
};

export function ConfidenceBadge({ value }: ConfidenceBadgeProps) {
  const low = value < LOW_CONFIDENCE;
  const percent = Math.round(value * 100);

  return (
    <span
      className={[
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-semibold",
        low ? "bg-warn/15 text-warn" : "bg-teal/10 text-teal",
      ].join(" ")}
    >
      {percent.toLocaleString("fa-IR")}٪{low ? " — بررسی" : ""}
    </span>
  );
}
