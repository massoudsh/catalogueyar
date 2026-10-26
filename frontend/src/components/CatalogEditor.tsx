import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { exportCatalog, type Marketplace } from "../lib/api";
import { LOW_CONFIDENCE } from "../lib/config";
import type { CatalogGenerateResponse } from "../lib/schemas";
import { ConfidenceBadge } from "./ConfidenceBadge";
import { StatusBanner } from "./StatusBanner";

type CatalogEditorProps = {
  catalog: CatalogGenerateResponse | null;
  draftId: string | null;
  busy: boolean;
  onSave: (next: CatalogGenerateResponse) => Promise<void>;
  onDirtyChange: (dirty: boolean) => void;
};

type TabKey = "attributes" | "variants" | "questions" | "english" | "seo" | "evidence";

export function CatalogEditor({ catalog, draftId, busy, onSave, onDirtyChange }: CatalogEditorProps) {
  const [draft, setDraft] = useState<CatalogGenerateResponse | null>(catalog);
  const [tab, setTab] = useState<TabKey>("attributes");
  const [message, setMessage] = useState<string | null>(null);
  const [keywords, setKeywords] = useState(catalog?.seo_keywords.join("، ") ?? "");
  const [exporting, setExporting] = useState(false);
  const [marketplace, setMarketplace] = useState<Marketplace>("digikala");
  const dirty = Boolean(draft) && JSON.stringify(draft) !== JSON.stringify(catalog);

  useEffect(() => {
    onDirtyChange(dirty);
    if (!dirty) return;
    const warn = (event: BeforeUnloadEvent) => {
      event.preventDefault();
      event.returnValue = "";
    };
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [dirty, onDirtyChange]);

  useEffect(() => {
    setDraft(catalog);
    setKeywords(catalog?.seo_keywords.join("، ") ?? "");
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
  const checks = [
    { label: "عنوان محصول را وارد کن.", passed: Boolean(draft.title.trim()) },
    { label: "توضیح محصول را وارد کن.", passed: Boolean(draft.description.trim()) },
    { label: "دستهٔ محصول و اطمینان آن را بررسی کن.", passed: Boolean(draft.category.suggested.trim()) && !categoryLow },
    { label: "ویژگی‌های خالی یا کم‌اطمینان را بازبینی کن.", passed: draft.attributes.length > 0 && draft.attributes.every((item) => item.value.trim() && item.confidence >= LOW_CONFIDENCE) },
    { label: "سؤال‌های باقی‌مانده را بررسی کن.", passed: draft.missing_info_questions.length === 0 },
  ];
  const score = Math.round(checks.filter((item) => item.passed).length / checks.length * 100);

  async function handleExport() {
    if (!draftId || dirty) return;
    setExporting(true);
    setMessage(null);
    try {
      const payload = await exportCatalog(draftId, marketplace);
      const url = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json;charset=utf-8" }));
      const link = document.createElement("a");
      link.href = url;
      link.download = `catalog-${draftId}-${marketplace}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } catch {
      setMessage("دریافت خروجی ناموفق بود؛ دوباره تلاش کن.");
    } finally {
      setExporting(false);
    }
  }

  async function handleSave() {
    if (!draft || !draftId) return;
    setMessage(null);
    await onSave(draft);
  }

  const tabs: { key: TabKey; label: string }[] = [
    { key: "attributes", label: "ویژگی‌ها" },
    { key: "variants", label: "واریانت‌ها" },
    { key: "questions", label: "سوال‌های ناقص" },
    { key: "english", label: "انگلیسی" },
    { key: "seo", label: "سئو و FAQ" },
    { key: "evidence", label: "منشأ اطلاعات" },
  ];

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="rounded-2xl border border-line/70 bg-paper/85 p-5 shadow-[0_20px_50px_-30px_rgba(16,42,41,0.45)] backdrop-blur md:p-7"
      aria-label="ویرایش کاتالوگ"
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
          aria-label="توضیح محصول"
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
            aria-pressed={tab === item.key}
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
                  aria-label={item.name}
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

      {tab === "seo" && (
        <div className="space-y-4 text-sm">
          <label className="block">
            <span className="text-xs text-ink-soft/70">توضیح کوتاه</span>
            <textarea
              value={draft.short_description}
              disabled={busy}
              rows={2}
              onChange={(event) => setDraft({ ...draft, short_description: event.target.value })}
              className="mt-1 w-full resize-y rounded-xl border border-line bg-mist/40 px-3 py-2.5 leading-7 outline-none ring-teal/30 focus:ring-2"
            />
          </label>
          <label className="block">
            <span className="text-xs text-ink-soft/70">کلیدواژه‌ها (با ویرگول جدا کن)</span>
            <input
              value={keywords}
              disabled={busy || exporting}
              onChange={(event) => {
                setKeywords(event.target.value);
                setDraft({ ...draft, seo_keywords: event.target.value.split(/[،,]/).map((item) => item.trim()).filter(Boolean) });
              }}
              className="mt-1 w-full rounded-lg border border-line bg-paper px-2.5 py-2 outline-none focus:border-teal"
            />
          </label>
          <div>
            <span className="text-xs text-ink-soft/70">پرسش‌های متداول</span>
            {draft.faqs.length === 0 ? (
              <p className="mt-1 text-ink-soft/70">پرسش متداولی تولید نشده.</p>
            ) : (
              <ul className="mt-2 space-y-2">
                {draft.faqs.map((item, index) => (
                  <li key={index} className="rounded-xl border border-line/60 px-3 py-2.5">
                    <label className="block">
                      <span className="text-xs text-ink-soft">پرسش {index + 1}</span>
                      <input value={item.question} disabled={busy || exporting}
                        onChange={(event) => setDraft({ ...draft, faqs: draft.faqs.map((faq, i) => i === index ? { ...faq, question: event.target.value } : faq) })}
                        className="mt-1 w-full rounded-lg border border-line bg-paper px-2.5 py-2 outline-none focus:border-teal" />
                    </label>
                    <label className="mt-2 block">
                      <span className="text-xs text-ink-soft">پاسخ</span>
                      <textarea value={item.answer} disabled={busy || exporting} rows={2}
                        onChange={(event) => setDraft({ ...draft, faqs: draft.faqs.map((faq, i) => i === index ? { ...faq, answer: event.target.value } : faq) })}
                        className="mt-1 w-full rounded-lg border border-line bg-paper px-2.5 py-2 leading-7 outline-none focus:border-teal" />
                    </label>
                    <button type="button" disabled={busy || exporting}
                      onClick={() => setDraft({ ...draft, faqs: draft.faqs.filter((_, i) => i !== index) })}
                      className="mt-2 rounded-lg px-2 py-1 text-xs text-danger hover:bg-danger/10 disabled:opacity-50">
                      حذف پرسش و پاسخ
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {tab === "evidence" && (
        <div className="space-y-3 text-sm">
          <p className="text-xs leading-6 text-ink-soft">این شواهد را مدل ثبت کرده است و راستی‌آزمایی مستقل محسوب نمی‌شود.</p>
          {([
            ["عکس محصول", draft.source_evidence.from_image],
            ["ویس فروشنده", draft.source_evidence.from_voice],
            ["متن روی بسته‌بندی", draft.source_evidence.from_text_on_package],
          ] as const).map(([label, items]) => (
            <div key={label}>
              <span className="text-xs text-ink-soft/70">{label}</span>
              {items.length === 0 ? (
                <p className="mt-1 text-ink-soft/60">شواهدی ثبت نشده.</p>
              ) : (
                <ul className="mt-1 list-inside list-disc space-y-1 leading-7 text-ink-soft">
                  {items.map((item, index) => <li key={`${item}-${index}`}>{item}</li>)}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}

      {draftId && (
        <div className="mt-6 flex flex-col gap-3 border-t border-line/60 pt-5">
          <div className="rounded-xl border border-line/60 bg-mist/30 px-3 py-3">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-semibold text-ink-soft">آمادگی برای انتشار</span>
              <span className="text-sm font-bold text-teal">{score.toLocaleString("fa-IR")}٪</span>
            </div>
            <ul className="mt-2 list-inside list-disc space-y-1 text-xs leading-6 text-ink-soft/80">
              {checks.filter((item) => !item.passed).map((item) => <li key={item.label}>{item.label}</li>)}
              {checks.every((item) => item.passed) && <li className="text-ok">همهٔ بررسی‌های اولیه موفق‌اند.</li>}
            </ul>
            <p className="mt-2 text-xs leading-6 text-ink-soft">این چک‌لیست تأیید صحت ادعاها یا پذیرش بازارگاه نیست؛ پیش از انتشار محتوا را بازبینی کن.</p>
          </div>
          <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
            <label>
              <span className="sr-only">بازارگاه</span>
              <select
                value={marketplace}
                disabled={exporting || dirty}
                onChange={(event) => setMarketplace(event.target.value as Marketplace)}
                className="w-full rounded-lg border border-line bg-paper px-2.5 py-2 text-sm outline-none focus:border-teal"
              >
                <option value="digikala">دیجی‌کالا</option>
                <option value="basalam">باسلام</option>
                <option value="torob">ترب</option>
              </select>
            </label>
            <button
              type="button"
              disabled={busy || exporting || dirty}
              onClick={() => void handleExport()}
              className="rounded-lg border border-teal px-3 py-2 text-sm font-semibold text-teal transition hover:bg-teal/10 disabled:opacity-50"
            >
              {exporting ? "در حال دریافت…" : "دریافت JSON کاتالوگ"}
            </button>
          </div>
          <p className="text-xs leading-6 text-ink-soft">خروجی عمومی برای اتصال سفارشی است؛ فرمت رسمی یا تأییدشدهٔ بازارگاه نیست و چیزی منتشر نمی‌شود.</p>
          {dirty && <p className="text-xs text-warn">برای خروجی معتبر، ابتدا اصلاحات را ذخیره کن.</p>}
          <p className="text-xs leading-6 text-ink-soft/70">
            فیلدهای کم‌اطمینان (زیر ۷۰٪) هایلایت شده‌اند؛ بعد از اصلاح ذخیره کن.
          </p>
          <button
            type="button"
            disabled={busy || exporting || !dirty}
            onClick={() => void handleSave()}
            className="rounded-xl bg-teal px-4 py-2.5 text-sm font-bold text-paper transition hover:bg-teal-bright disabled:opacity-60"
          >
            {busy ? "در حال ذخیره…" : dirty ? "ذخیرهٔ اصلاحات" : "همهٔ تغییرات ذخیره شده"}
          </button>
          {message && <StatusBanner message={message} tone="error" />}
        </div>
      )}
    </motion.section>
  );
}
