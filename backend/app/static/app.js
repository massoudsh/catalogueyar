const form = document.querySelector("#catalog-form");
const imageInput = document.querySelector("#images");
const imageSummary = document.querySelector("#image-summary");
const statusBox = document.querySelector("#status");
const title = document.querySelector("#result-title");
const description = document.querySelector("#result-description");
const category = document.querySelector("#result-category");
const confidence = document.querySelector("#result-confidence");
const panels = {
  attributes: document.querySelector("#attributes"),
  variants: document.querySelector("#variants"),
  questions: document.querySelector("#questions"),
};

const setStatus = (message, state = "") => {
  statusBox.textContent = message;
  statusBox.className = `notice ${state}`.trim();
};

const renderList = (items, renderer) => {
  if (!items || items.length === 0) return '<p class="empty">موردی برای نمایش وجود ندارد.</p>';
  return `<ul class="list">${items.map(renderer).join("")}</ul>`;
};

const renderResult = (data) => {
  title.textContent = data.title || "کاتالوگ بدون عنوان";
  description.textContent = data.description || "توضیحی تولید نشده است.";
  category.textContent = data.category?.suggested || "—";
  confidence.textContent = data.category?.confidence === undefined ? "—" : `${Math.round(data.category.confidence * 100)}٪`;

  panels.attributes.innerHTML = renderList(
    data.attributes,
    (item) => `<li><span>${item.name}</span><strong>${item.value}</strong><span class="badge">${Math.round(item.confidence * 100)}٪</span></li>`
  );
  panels.variants.innerHTML = renderList(
    data.variants,
    (item) => `<li><span>${item.type}</span><strong>${item.options.join("، ")}</strong></li>`
  );
  panels.questions.innerHTML = renderList(
    data.missing_info_questions,
    (item) => `<li><span>${item}</span></li>`
  );
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

  const categories = document.querySelector("#categories").value.split(/[،,]/).map((item) => item.trim()).filter(Boolean);
  categories.forEach((item) => body.append("store_category_list", item));

  setStatus("در حال تحلیل رسانه‌ها و ساخت کاتالوگ…");

  try {
    const response = await fetch("/catalog/generate", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "ساخت کاتالوگ ناموفق بود.");
    renderResult(data);
    setStatus("کاتالوگ با موفقیت ساخته شد.", "is-success");
  } catch (error) {
    setStatus(error.message, "is-error");
  }
});
