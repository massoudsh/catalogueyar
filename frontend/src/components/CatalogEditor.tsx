import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { LOW_CONFIDENCE } from "../lib/config";
import type { CatalogGenerateResponse } from "../lib/schemas";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { StatusBanner } from "./StatusBanner";

type CatalogEditorProps = {
  catalog: CatalogGenerateResponse | null;
  draftId: string | null;
  busy: boolean;
  onSave: (next: CatalogGenerateResponse) => Promise<void>;
};

type TabKey = "attributes" | "variants" | "questions" | "english";

export function CatalogEditor({ catalog, draftId, busy, onSave }: CatalogEditorProps) {
  const [draft, setDraft] = useState<CatalogGenerateResponse | null>(catalog);
  const [tab, setTab] = useState<TabKey>("attributes");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    setDraft(catalog);
    setMessage(null);
  }, [catalog]);

  if (!draft) {
    return (
      <section className="rounded-2xl border border-line/60 bg-paper/55 p-6 md:p-8">
        <p className="text-xs font-semibold text-teal">پیش‌نمایش خروجی</p>
        <h2 className="mt-1 text-xl font-bold text-ink">کاتالوگ هنوز ساخته نشده</h2>
        <p className="mt-3 text-sm leading-7 text-ink-soft/80">
          بعد از تولید، عنوان، دسته، توضیح و ویژگی‌ها اینجا قابل ویرایش می‌شوند.
        </p>
      </section>
    );
  }

  const categoryLow = draft.category.confidence < LOW_CONFIDENCE;

  async function handleSave() {
    if (!draft || !draftId) return;
    setMessage(null);
    await onSave(draft);
    setMessage("اصلاحات ذخیره شد و در یادگیری بعدی فروشنده استفاده می‌شود.");
  }

  const tabs: { key: TabKey; label: string }[] = [
    { key: "attributes", label: "ویژگی‌ها" },
    { key: "variants", label: "واریانت‌ها" },
    { key: "questions", label: "سوال‌های ناقص" },
    { key: "english", label: "انگلیسی" },
  ];

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="rounded-2xl border border-line/70 bg-paper/85 p-5 shadow-[0_20px_50px_-30px_rgba(16,42,41,0.45)] backdrop-blur md:p-7"
      aria-live="polite"
    >
      <div className="mb-5">
        <p className="text-xs font-semibold text-teal">حالت ویرایش</p>
        <label className="mt-2 block">
          <span className="sr-only">عنوان</span>
          <input
            value={draft.title}
            disabled={busy}
            onChange={(event) => setDraft({ ...draft, title: event.target.value })}
            className="w-full border-0 border-b border-line bg-transparent pb-2 text-xl font-bold text-ink outline-none focus:border-teal"
          />
        </label>
        <textarea
          value={draft.description}
          disabled={busy}
          rows={3}
          onChange={(event) => setDraft({ ...draft, description: event.target.value })}
          className="mt-3 w-full resize-y rounded-xl border border-line bg-mist/40 px-3 py-2.5 text-sm leading-7 outline-none ring-teal/30 focus:ring-2"
        />
      </div>

      <div
        className={[
          "mb-5 grid gap-3 rounded-xl border px-4 py-3 sm:grid-cols-2",
          categoryLow ? "border-warn/40 bg-warn/5" : "border-line/70 bg-mist/40",
        ].join(" ")}
      >
        <label>
          <span className="text-xs text-ink-soft/70">دسته پیشنهادی</span>
          <input
            value={draft.category.suggested}
            disabled={busy}
            onChange={(event) =>
              setDraft({
                ...draft,
                category: {
                  suggested: event.target.value,
                  confidence: 1,
                },
              })
            }
            className="mt-1 w-full rounded-lg border border-line bg-paper px-2.5 py-2 text-sm font-semibold outline-none focus:border-teal"
          />
        </label>
        <div className="flex items-end justify-between gap-2 sm:justify-start sm:gap-3">
          <div>
            <span className="text-xs text-ink-soft/70">اعتماد</span>
            <div className="mt-2">
              <ConfidenceBadge value={draft.category.confidence} />
            </div>
          </div>
          {draftId && (
            <span className="text-xs text-ink-soft/55">draft: {draftId.slice(0, 8)}…</span>
          )}
        </div>
      </div>

      <div className="mb-4 flex flex-wrap gap-2">
        {tabs.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setTab(item.key)}
            className={[
              "rounded-lg px-3 py-1.5 text-xs font-semibold transition",
              tab === item.key
                ? "bg-teal text-paper"
                : "bg-mist text-ink-soft hover:bg-mist-deep",
            ].join(" ")}
          >
            {item.label}
          </button>
        ))}
      </div>

      {tab === "attributes" && (
        <ul className="space-y-3">
          {draft.attributes.length === 0 && (
            <li className="text-sm text-ink-soft/70">موردی برای نمایش وجود ندارد.</li>
          )}
          {draft.attributes.map((item, index) => {
            const low = item.confidence < LOW_CONFIDENCE;
            return (
              <li
                key={`${item.name}-${index}`}
                className={[
                  "rounded-xl border px-3 py-3",
                  low ? "border-warn/35 bg-warn/5" : "border-line/60",
                ].join(" ")}
              >
                <div className="mb-2 flex items-center justify-between gap-2">
                  <span className="text-sm font-semibold text-ink">{item.name}</span>
                  <ConfidenceBadge value={item.confidence} />
                </div>
                <input
                  value={item.value}
                  disabled={busy}
                  onChange={(event) => {
                    const attributes = draft.attributes.map((attr, attrIndex) =>
                      attrIndex === index
                        ? { ...attr, value: event.target.value, confidence: 1 }
                        : attr,
                    );
                    setDraft({ ...draft, attributes });
                  }}
                  className="w-full rounded-lg border border-line bg-paper px-2.5 py-2 text-sm outline-none focus:border-teal"
                />
              </li>
            );
          })}
        </ul>
      )}

      {tab === "variants" && (
        <ul className="space-y-2">
          {draft.variants.length === 0 && (
            <li className="text-sm text-ink-soft/70">موردی برای نمایش وجود ندارد.</li>
          )}
          {draft.variants.map((item, index) => (
            <li
              key={`${item.type}-${index}`}
              className="flex flex-wrap items-baseline justify-between gap-2 rounded-xl border border-line/60 px-3 py-2.5 text-sm"
            >
              <span className="font-medium text-ink-soft">{item.type}</span>
              <strong className="font-semibold text-ink">{item.options.join("، ")}</strong>
            </li>
          ))}
        </ul>
      )}

      {tab === "questions" && (
        <ul className="space-y-2">
          {draft.missing_info_questions.length === 0 && (
            <li className="text-sm text-ink-soft/70">سوال ناقصی باقی نمانده.</li>
          )}
          {draft.missing_info_questions.map((question) => (
            <li
              key={question}
              className="rounded-xl border border-line/60 px-3 py-2.5 text-sm leading-7 text-ink"
            >
              {question}
            </li>
          ))}
        </ul>
      )}

      {tab === "english" && (
        <div className="space-y-3 text-sm">
          {draft.english ? (
            <>
              <div>
                <span className="text-xs text-ink-soft/70">Title</span>
                <p className="mt-1 font-semibold text-ink" dir="ltr">
                  {draft.english.title || "—"}
                </p>
              </div>
              <div>
                <span className="text-xs text-ink-soft/70">Description</span>
                <p className="mt-1 leading-7 text-ink-soft" dir="ltr">
                  {draft.english.description || "—"}
                </p>
              </div>
            </>
          ) : (
            <p className="text-ink-soft/70">نسخه انگلیسی در پاسخ موجود نیست.</p>
          )}
        </div>
      )}

      {draftId && (
        <div className="mt-6 flex flex-col gap-3 border-t border-line/60 pt-5">
          <p className="text-xs leading-6 text-ink-soft/70">
            فیلدهای کم‌اطمینان (زیر ۷۰٪) هایلایت شده‌اند؛ بعد از اصلاح ذخیره کن.
          </p>
          <button
            type="button"
            disabled={busy}
            onClick={() => void handleSave()}
            className="rounded-xl bg-teal px-4 py-2.5 text-sm font-bold text-paper transition hover:bg-teal-bright disabled:opacity-60"
          >
            {busy ? "در حال ذخیره…" : "ذخیرهٔ اصلاحات"}
          </button>
          {message && <StatusBanner message={message} tone="ok" />}
        </div>
      )}
    </motion.section>
  );
}
