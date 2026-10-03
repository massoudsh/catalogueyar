const LOW_CONFIDENCE = 0.7;

const form = document.querySelector("#catalog-form");
const imageInput = document.querySelector("#images");
const imageSummary = document.querySelector("#image-summary");
const statusBox = document.querySelector("#status");
const title = document.querySelector("#result-title");
const description = document.querySelector("#result-description");
const category = document.querySelector("#result-category");
const confidence = document.querySelector("#result-confidence");
const categoryMeta = document.querySelector("#category-meta");
const editActions = document.querySelector("#edit-actions");
const saveEdits = document.querySelector("#save-edits");
const panels = {
  attributes: document.querySelector("#attributes"),
  variants: document.querySelector("#variants"),
  questions: document.querySelector("#questions"),
};

let currentDraftId = null;
let currentCatalog = null;

const setStatus = (message, state = "") => {
  statusBox.textContent = message;
  statusBox.className = `notice ${state}`.trim();
};

const isLow = (value) => typeof value === "number" && value < LOW_CONFIDENCE;

const renderList = (items, renderer) => {
  if (!items || items.length === 0) return '<p class="empty">موردی برای نمایش وجود ندارد.</p>';
  return `<ul class="list">${items.map(renderer).join("")}</ul>`;
};

const renderResult = (data) => {
  currentCatalog = data;
  currentDraftId = data.draft_id || null;

  title.textContent = data.title || "کاتالوگ بدون عنوان";
  description.textContent = data.description || "توضیحی تولید نشده است.";
  category.textContent = data.category?.suggested || "—";
  confidence.textContent =
    data.category?.confidence === undefined ? "—" : `${Math.round(data.category.confidence * 100)}٪`;

  categoryMeta.classList.toggle("is-low-confidence", isLow(data.category?.confidence));
  editActions.classList.toggle("is-hidden", !currentDraftId);

  panels.attributes.innerHTML = renderList(data.attributes, (item, index) => {
    const low = isLow(item.confidence);
    if (low && currentDraftId) {
      return `<li class="is-low-confidence" data-attr-index="${index}">
        <label class="edit-field">
          <span>${item.name}</span>
          <input data-attr-value="${index}" value="${item.value.replaceAll('"', "&quot;")}" />
        </label>
        <span class="badge badge--warn">${Math.round(item.confidence * 100)}٪ — نیاز به تأیید</span>
      </li>`;
    }
    return `<li class="${low ? "is-low-confidence" : ""}">
      <span>${item.name}</span>
      <strong>${item.value}</strong>
      <span class="badge ${low ? "badge--warn" : ""}">${Math.round(item.confidence * 100)}٪${low ? " — بررسی" : ""}</span>
    </li>`;
  });

  panels.variants.innerHTML = renderList(
    data.variants,
    (item) => `<li><span>${item.type}</span><strong>${item.options.join("، ")}</strong></li>`
  );
  panels.questions.innerHTML = renderList(
    data.missing_info_questions,
    (item) => `<li><span>${item}</span></li>`
  );

  if (currentDraftId && isLow(data.category?.confidence)) {
    category.innerHTML = `<input id="edit-category" value="${(data.category?.suggested || "").replaceAll('"', "&quot;")}" />`;
  }
};

imageInput.addEventListener("change", () => {
  const count = imageInput.files.length;
  imageSummary.textContent = count ? `${count.toLocaleString("fa-IR")} فایل انتخاب شد` : "هنوز فایلی انتخاب نشده";
});

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((item) => item.classList.remove("is-active"));
    Object.values(panels).forEach((panel) => panel.classList.add("is-hidden"));
    tab.classList.add("is-active");
    panels[tab.dataset.tab].classList.remove("is-hidden");
  });
});

saveEdits?.addEventListener("click", async () => {
  if (!currentDraftId || !currentCatalog) return;

  const attributes = (currentCatalog.attributes || []).map((item, index) => {
    const input = document.querySelector(`[data-attr-value="${index}"]`);
    return {
      ...item,
      value: input ? input.value.trim() : item.value,
      confidence: input ? 1 : item.confidence,
    };
  });

  const categoryInput = document.querySelector("#edit-category");
  const body = {
    attributes,
    category: categoryInput
      ? { suggested: categoryInput.value.trim(), confidence: 1 }
      : currentCatalog.category,
  };

  setStatus("در حال ذخیرهٔ اصلاحات…");
  try {
    const response = await fetch(`/catalog/${currentDraftId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "ذخیرهٔ اصلاحات ناموفق بود.");
    renderResult({ ...data.catalog, draft_id: data.id });
    setStatus("اصلاحات ذخیره شد و در یادگیری بعدی فروشنده استفاده می‌شود.", "is-success");
  } catch (error) {
    setStatus(error.message, "is-error");
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  if (imageInput.files.length < 1 || imageInput.files.length > 5) {
    setStatus("باید بین ۱ تا ۵ عکس یا ویدئو انتخاب کنی.", "is-error");
    return;
  }

  const body = new FormData();
  [...imageInput.files].forEach((file) => body.append("images", file));

  const voice = document.querySelector("#voice_note").files[0];
  if (voice) body.append("voice_note", voice);

  const hint = document.querySelector("#seller_hint").value.trim();
  if (hint) body.append("seller_hint", hint);

  const categories = document
    .querySelector("#categories")
    .value.split(/[،,]/)
    .map((item) => item.trim())
    .filter(Boolean);
  categories.forEach((item) => body.append("store_category_list", item));

  setStatus("در حال تحلیل رسانه‌ها و ساخت کاتالوگ…");

  try {
    const response = await fetch("/catalog/generate", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "ساخت کاتالوگ ناموفق بود.");
    renderResult(data);
    const lowCount = (data.attributes || []).filter((item) => isLow(item.confidence)).length;
    const note = lowCount || isLow(data.category?.confidence)
      ? " فیلدهای کم‌اطمینان برای تأیید هایلایت شدند."
      : "";
    setStatus(`کاتالوگ با موفقیت ساخته شد.${note}`, "is-success");
  } catch (error) {
    setStatus(error.message, "is-error");
  }
});
