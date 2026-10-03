import { motion } from "framer-motion";
import type { CatalogDraft } from "../lib/schemas";

type HistoryListProps = {
  drafts: CatalogDraft[];
  activeId: string | null;
  onSelect: (draft: CatalogDraft) => void;
  onRefresh: () => void;
  busy?: boolean;
};

export function HistoryList({
  drafts,
  activeId,
  onSelect,
  onRefresh,
  busy = false,
}: HistoryListProps) {
  return (
    <motion.aside
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.05 }}
      className="rounded-2xl border border-line/60 bg-paper/60 p-4 backdrop-blur"
    >
      <div className="mb-3 flex items-center justify-between gap-2">
        <h3 className="text-sm font-bold text-ink">تاریخچه draftها</h3>
        <button
          type="button"
          onClick={onRefresh}
          disabled={busy}
          className="text-xs font-semibold text-teal hover:underline disabled:opacity-50"
        >
          تازه‌سازی
        </button>
      </div>

      {drafts.length === 0 ? (
        <p className="text-xs leading-6 text-ink-soft/70">هنوز draftی ذخیره نشده.</p>
      ) : (
        <ul className="max-h-64 space-y-2 overflow-y-auto">
          {drafts.map((draft) => {
            const active = draft.id === activeId;
            return (
              <li key={draft.id}>
                <button
                  type="button"
                  onClick={() => onSelect(draft)}
                  className={[
                    "w-full rounded-xl px-3 py-2.5 text-right transition",
                    active ? "bg-teal text-paper" : "bg-mist/80 hover:bg-mist-deep text-ink",
                  ].join(" ")}
                >
                  <span className="block truncate text-sm font-semibold">
                    {draft.catalog.title || "بدون عنوان"}
                  </span>
                  <span
                    className={[
                      "mt-1 block text-[11px]",
                      active ? "text-paper/75" : "text-ink-soft/65",
                    ].join(" ")}
                  >
                    {new Date(draft.updated_at).toLocaleString("fa-IR")}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </motion.aside>
  );
}
