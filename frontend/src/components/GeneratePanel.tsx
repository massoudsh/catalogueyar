import { useMemo, useState, type FormEvent } from "react";
import { motion } from "framer-motion";
import { GenerateFormSchema } from "../lib/schemas";
import { StatusBanner } from "./StatusBanner";

export type GenerateSubmitPayload = {
  images: File[];
  voiceNote: File | null;
  sellerHint: string;
  storeCategories: string[];
};

type GeneratePanelProps = {
  busy: boolean;
  onSubmit: (payload: GenerateSubmitPayload) => Promise<void>;
};

function splitCategories(raw: string): string[] {
  return raw
    .split(/[،,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export function GeneratePanel({ busy, onSubmit }: GeneratePanelProps) {
  const [images, setImages] = useState<File[]>([]);
  const [voiceNote, setVoiceNote] = useState<File | null>(null);
  const [sellerHint, setSellerHint] = useState("");
  const [categories, setCategories] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const imageSummary = useMemo(() => {
    if (images.length === 0) return "هنوز فایلی انتخاب نشده";
    return `${images.length.toLocaleString("fa-IR")} فایل انتخاب شد`;
  }, [images.length]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setLocalError(null);

    const parsed = GenerateFormSchema.safeParse({
      mediaCount: images.length,
      sellerHint,
      categories,
    });

    if (!parsed.success) {
      setLocalError(parsed.error.issues[0]?.message ?? "ورودی نامعتبر است");
      return;
    }

    await onSubmit({
      images,
      voiceNote,
      sellerHint,
      storeCategories: splitCategories(categories),
    });
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="rounded-2xl border border-line/70 bg-paper/80 p-5 shadow-[0_20px_50px_-30px_rgba(16,42,41,0.45)] backdrop-blur md:p-7"
    >
      <div className="mb-6">
        <p className="text-xs font-semibold tracking-wide text-teal">ساخت draft</p>
        <h2 className="mt-1 text-xl font-bold text-ink">رسانه محصول را بارگذاری کن</h2>
        <p className="mt-2 text-sm leading-7 text-ink-soft/80">
          عکس یا ویدئو ضروری است؛ ویس، توضیح فروشنده و دسته‌های مجاز اختیاری‌اند.
        </p>
      </div>

      <label className="group flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-teal/35 bg-mist/60 px-4 py-10 text-center transition hover:border-teal hover:bg-mist-deep/50">
        <input
          type="file"
          accept="image/*,video/*"
          multiple
          className="sr-only"
          disabled={busy}
          onChange={(event) => {
            const files = [...(event.target.files ?? [])].slice(0, 5);
            setImages(files);
          }}
        />
        <span className="mb-2 flex size-11 items-center justify-center rounded-full bg-teal/10 text-2xl font-light text-teal transition group-hover:bg-teal group-hover:text-paper">
          +
        </span>
        <strong className="text-sm text-ink">عکس یا ویدئوی محصول را انتخاب کن</strong>
        <small className="mt-1 text-xs text-ink-soft/70">حداقل ۱ و حداکثر ۵ رسانه</small>
        <span className="mt-3 text-sm font-medium text-teal">{imageSummary}</span>
      </label>

      {images.length > 0 && (
        <ul className="mt-3 space-y-1 text-xs text-ink-soft/75">
          {images.map((file) => (
            <li key={`${file.name}-${file.size}`}>{file.name}</li>
          ))}
        </ul>
      )}

      <label className="mt-5 block">
        <span className="mb-1.5 block text-sm font-medium text-ink-soft">ویس فارسی اختیاری</span>
        <input
          type="file"
          accept="audio/*"
          disabled={busy}
          className="w-full rounded-xl border border-line bg-paper px-3 py-2.5 text-sm file:ml-3 file:rounded-lg file:border-0 file:bg-teal/10 file:px-3 file:py-1.5 file:text-sm file:font-semibold file:text-teal"
          onChange={(event) => setVoiceNote(event.target.files?.[0] ?? null)}
        />
      </label>

      <label className="mt-4 block">
        <span className="mb-1.5 block text-sm font-medium text-ink-soft">توضیح فروشنده</span>
        <textarea
          rows={4}
          disabled={busy}
          value={sellerHint}
          onChange={(event) => setSellerHint(event.target.value)}
          placeholder="مثلاً: کیف چرمی زنانه، مناسب استفاده روزمره، بند قابل تنظیم"
          className="w-full resize-y rounded-xl border border-line bg-paper px-3 py-2.5 text-sm leading-7 outline-none ring-teal/30 focus:ring-2"
        />
      </label>

      <label className="mt-4 block">
        <span className="mb-1.5 block text-sm font-medium text-ink-soft">
          دسته‌های مجاز فروشگاه
        </span>
        <input
          type="text"
          disabled={busy}
          value={categories}
          onChange={(event) => setCategories(event.target.value)}
          placeholder="کیف، اکسسوری، پوشاک"
          className="w-full rounded-xl border border-line bg-paper px-3 py-2.5 text-sm outline-none ring-teal/30 focus:ring-2"
        />
        <small className="mt-1 block text-xs text-ink-soft/65">با ویرگول جدا کن.</small>
      </label>

      <button
        type="submit"
        disabled={busy}
        className="mt-6 w-full rounded-xl bg-saffron px-4 py-3 text-sm font-bold text-ink transition hover:bg-saffron-soft disabled:cursor-not-allowed disabled:opacity-60"
      >
        {busy ? "در حال تولید…" : "تولید کاتالوگ"}
      </button>

      {localError && (
        <div className="mt-4">
          <StatusBanner message={localError} tone="error" />
        </div>
      )}
    </motion.form>
  );
}
